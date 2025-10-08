# --------------------------------------
# Supabase service role verification (recommended)
# --------------------------------------

def verify_supabase_user_via_service_role(auth_header: Optional[str]) -> Optional[Dict[str, Any]]:
    """Resolve user session using Supabase service role key instead of local JWT verification.
    Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.

    Returns a dict with user info if valid, otherwise None.
    """
    try:
        if not (Config.SUPABASE_URL and Config.SUPABASE_SERVICE_ROLE_KEY and auth_header):
            return None
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        access_token = parts[1]
        url = Config.SUPABASE_URL.rstrip('/') + '/auth/v1/user'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'apikey': Config.SUPABASE_SERVICE_ROLE_KEY,
        }
        r = httpx.get(url, headers=headers, timeout=5.0)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception as e:
        logger.debug(f"Supabase service role verify failed: {e}")
        return None
