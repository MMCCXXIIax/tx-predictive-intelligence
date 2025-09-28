# Gunicorn configuration for TX Trade Whisperer
import os

# Server socket
# Dynamic port binding for Render compatibility
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
backlog = 2048

# Worker processes (use gthread to avoid gevent monkey-patching warnings)
workers = int(os.environ.get('WEB_CONCURRENCY', 1))
worker_class = 'gthread'
threads = int(os.environ.get('THREADS', 4))
timeout = int(os.environ.get('GUNICORN_TIMEOUT', 60))
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'tx-trade-whisperer'

# Server mechanics
preload_app = False
daemon = False
pidfile = None
tmp_upload_dir = None

# SSL (if needed)
keyfile = None
certfile = None
