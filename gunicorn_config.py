"""
Конфигурация gunicorn для Flask-SocketIO с gevent
"""
import multiprocessing

# Количество worker процессов
workers = 1  # Flask-SocketIO требует 1 worker для правильной работы комнат

# Worker класс для gevent (лучше работает с gunicorn)
worker_class = 'gevent'

# Количество одновременных соединений на worker
worker_connections = 1000

# Таймауты
timeout = 60
keepalive = 2

# Биндинг
bind = '0.0.0.0:8000'

# Логирование
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Перезагрузка при изменении кода (только для разработки)
reload = False

