import os
import requests
from sqlalchemy.orm import Session
from models import Profile  # adjust import to your project

SAVE_PROFILE_MODE = os.getenv("SAVE_PROFILE_MODE", "db").lower()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def save_profile(session: Session, user_id, name, email, mode_value):
    """Save profile using either DB or REST based on mode."""
    if SAVE_PROFILE_MODE == "db":
        return _save_via_db(session, user_id, name, email, mode_value)
    else:
        return _save_via_rest(user_id, name, email, mode_value)

def _save_via_db(session: Session, user_id, name, email, mode_value):
    profile = session.query(Profile).filter_by(id=user_id).first()
    if profile:
        profile.name = name
        profile.email = email
        profile.mode = mode_value
    else:
        profile = Profile(id=user_id, name=name, email=email, mode=mode_value)
        session.add(profile)
    session.commit()
    return {"status": "ok", "method": "db"}

def _save_via_rest(user_id, name, email, mode_value):
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "id": user_id,
        "name": name,
        "email": email,
        "mode": mode_value
    }
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/profiles",
        headers=headers,
        json=payload,
        params={"on_conflict": "id", "upsert": "true"}
    )
    if resp.status_code in (200, 201):
        return {"status": "ok", "method": "rest"}
    else:
        return {"status": "error", "message": resp.text, "method": "rest"}
