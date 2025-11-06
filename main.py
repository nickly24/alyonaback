"""
Точка входа для gunicorn на Timeweb
Flask-SocketIO с eventlet требует специальной настройки для gunicorn
"""
from app import app, socketio

# Для gunicorn с eventlet worker нужно экспортировать app
# Flask-SocketIO будет работать через eventlet worker класс
# В gunicorn_config.py указан worker_class = 'eventlet'
application = app

