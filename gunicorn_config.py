# gunicorn_config.py

bind = '0.0.0.0:8000'
workers = 3
timeout = 30
keepalive = 2
