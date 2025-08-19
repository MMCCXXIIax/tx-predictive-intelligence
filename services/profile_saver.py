# services/profile_saver.py
import os
import requests
from sqlalchemy import text
from main import engine  # <-- now importing from your actual main.py

import os
from sqlalchemy import create_engine

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

# Recommended for Postgres on cloud poolers
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
    future=True,
)

SAVE_PROFILE_MODE = os.getenv("SAVE_PROFILE_MODE", "db").lower()

SUPABASE_URL = os.getenvSUPABASE_SERVICE("SUPABASE_URL")
_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


def save_profile(_session_unused, user_id, name, email, mode_value):
    """Save profile via DB (raw SQL) or Supabase REST. First arg kept for compatibility."""
    if SAVE_PROFILE_MODE == "db":
        return _save_via_db(user_id, name, email, mode_value)
    else:
        return _save_via_rest(user_id, name, email, mode_value)


def _save_via_db(user_id, name, email, mode_value):
    """Upsert into profiles table via raw SQL."""
    query = text("""
        INSERT INTO profiles (id, name, email, mode)
        VALUES (:id, :name, :email, :mode)
        ON CONFLICT (id) DO UPDATE
        SET name = EXCLUDED.name,
            email = EXCLUDED.email,
            mode = EXCLUDED.mode
    """)
    try:
        with engine.begin() as conn:
            conn.execute(query, {
                "id": user_id,
                "name": name,
                "email": email,
                "mode": mode_value
            })
        return {"status": "ok", "method": "db"}
    except Exception as e:
        return {"status": "error", "message": str(e), "method": "db"}


def _save_via_rest(user_id, name, email, mode_value):
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
        "name": name,
        "email": email,
        "mode": mode_value
    }

       requests.post try:
           resp(
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
