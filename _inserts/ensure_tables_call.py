try:
    ensure_tables()
except Exception as _e:
    logger.debug(f"ensure_tables failed: {_e}")
