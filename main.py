"""
Точка входа для gunicorn на Timeweb
Flask-SocketIO с gevent работает лучше с gunicorn
"""
from app import app, socketio

# Для gunicorn с gevent worker нужно экспортировать app
# Flask-SocketIO будет работать через gevent worker класс
# В gunicorn_config.py указан worker_class = 'gevent'
application = app

