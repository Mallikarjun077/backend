# gunicorn.py or gunicorn_conf.py

bind = "0.0.0.0:8000"                     # Address and port
workers = 4                               # Number of worker processes
worker_class = "uvicorn.workers.UvicornWorker"  # Use uvicorn worker for FastAPI
timeout = 120                             # Worker timeout
loglevel = "info"                         # Log level
