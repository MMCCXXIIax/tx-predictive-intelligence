# Gunicorn configuration for TX Trade Whisperer
import os

# Server socket
port = int(os.environ.get('PORT', 5000))
bind = f"0.0.0.0:{port}"
backlog = 2048

# Worker processes
workers = int(os.environ.get('WEB_CONCURRENCY', 2))
worker_class = 'gevent'
worker_connections = 1000
timeout = 30
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
preload_app = True
daemon = False
pidfile = None
tmp_upload_dir = None

# SSL (if needed)
keyfile = None
certfile = None
