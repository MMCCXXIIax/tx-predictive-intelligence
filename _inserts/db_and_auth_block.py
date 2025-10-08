# Database setup
engine = None
Session = None
db_available = False

def init_database():
    """Initialize database connection with fallback handling"""
    global engine, Session, db_available
    try:
        if Config.DATABASE_URL:
            # Force psycopg driver for PostgreSQL
            db_url = Config.DATABASE_URL
            if db_url.startswith('postgresql://') and 'psycopg' not in db_url:
                db_url = db_url.replace('postgresql://', 'postgresql+psycopg://')
            if db_url.startswith('postgres://'):
                db_url = db_url.replace('postgres://', 'postgresql+psycopg://', 1)
            # Ensure prepare_threshold=0 in URL for PgBouncer compatibility
            if 'postgresql+psycopg://' in db_url and 'prepare_threshold=' not in db_url:
                sep = '&' if '?' in db_url else '?'
                db_url = f"{db_url}{sep}prepare_threshold=0"

            _connect_args = {"sslmode": "require"} if db_url.startswith('postgresql') else {}
            if '+psycopg' in db_url:
                _connect_args["prepare_threshold"] = None

            _poolclass = NullPool if Config.USE_PGBOUNCER else QueuePool
            engine_kwargs = {
                'poolclass': _poolclass,
                'pool_pre_ping': True,
                'pool_recycle': 1800,
                'connect_args': _connect_args
            }
            if _poolclass is QueuePool:
                engine_kwargs['pool_size'] = 2
                engine_kwargs['max_overflow'] = 0

            engine = create_engine(db_url, **engine_kwargs)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            Session = scoped_session(sessionmaker(bind=engine))
            db_available = True
            logger.info("Database connection established successfully")

            # Create tables if they don't exist
            create_tables()
        else:
            logger.warning("No DATABASE_URL provided, running in demo mode")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        logger.info("Running in demo mode without database")

# Initialize database on startup
init_database()
try:
    ensure_tables()
except Exception as _e:
    logger.debug(f"ensure_tables failed: {_e}")

# --------------------------------------
# Optional Supabase service-role verification
# --------------------------------------

def verify_supabase_user_via_service_role(auth_header: Optional[Dict[str, Any]]):
    """Resolve user via Supabase Auth Admin using service role key.
    Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.
    Returns user dict or None.
    """
    try:
        if not (Config.SUPABASE_URL and Config.SUPABASE_SERVICE_ROLE_KEY and auth_header):
            return None
        if isinstance(auth_header, str):
            header_val = auth_header
        else:
            header_val = auth_header.get('Authorization') if isinstance(auth_header, dict) else None
        if not header_val:
            return None
        parts = header_val.split()
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

# Backward-compatible shim

def verify_supabase_jwt(auth_header: Optional[str]) -> Optional[Dict[str, Any]]:
    return verify_supabase_user_via_service_role(auth_header)
