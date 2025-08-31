import os
import requests
from sqlalchemy import text
from services.db import engine

SAVE_PROFILE_MODE = os.getenv("SAVE_PROFILE_MODE", "db").lower()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def save_profile(_session_unused, user_id, username, name, email, mode_value):
    """Save profile via DB (raw SQL) or Supabase REST."""
    # Auto-generate username if missing
    if not username:
        username = name or (email.split("@")[0] if email else None) or f"user_{user_id[:8]}"

    if SAVE_PROFILE_MODE == "db":
        return _save_via_db(user_id, username, name, email, mode_value)
    else:
        return _save_via_rest(user_id, username, name, email, mode_value)

def _save_via_db(user_id, username, name, email, mode_value):
    """Upsert into profiles table via raw SQL."""
    query = text("""
        INSERT INTO profiles (id, username, name, email, mode)
        VALUES (:id, :username, :name, :email, :mode)
        ON CONFLICT (id) DO UPDATE
        SET username = EXCLUDED.username,
            name = EXCLUDED.name,
            email = EXCLUDED.email,
            mode = EXCLUDED.mode
    """)
    try:
        with engine.begin() as conn:
            conn.execute(query, {
                "id": user_id,
                "username": username,
                "name": name,
                "email": email,
                "mode": mode_value
            })
        return {"status": "ok", "method": "db"}
    except Exception as e:
        return {"status": "error", "message": str(e), "method": "db"}

def _save_via_rest(user_id, username, name, email, mode_value):
    """Upsert via Supabase PostgREST."""
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        return {
            "status": "error",
            "message": "Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY",
            "method": "rest"
        }
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    payload = {
        "id": user_id,
        "username": username,
        "name": name,
        "email": email,
        "mode": mode_value
    }
    try:
        resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/profiles",
            headers=headers,
            json=payload,
            params={"on_conflict": "id"},
            timeout=10
        )
        if resp.status_code in (200, 201, 204):
            return {"status": "ok", "method": "rest"}
        else:
            return {"status": "error", "message": resp.text, "method": "rest"}
    except requests.RequestException as e:
        return {"status": "error", "message": str(e), "method": "rest"}
