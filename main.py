"""
Точка входа для gunicorn на Timeweb
Flask-SocketIO с threading режимом работает стабильно с gunicorn sync worker
"""
from app import app, socketio

# Для gunicorn с sync worker нужно экспортировать app
# Flask-SocketIO работает в threading режиме, который совместим с sync worker
# В gunicorn_config.py указан worker_class = 'sync' с threads
application = app

