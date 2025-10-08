# Backward-compatible shim: prefer service role verification over local JWT decode

def verify_supabase_jwt(auth_header: Optional[str]) -> Optional[Dict[str, Any]]:
    """Deprecated: use verify_supabase_user_via_service_role.
    This shim routes calls to the service-role-backed verification so existing
    call sites continue to work.
    """
    return verify_supabase_user_via_service_role(auth_header)
