"""
Конфигурация gunicorn для Flask-SocketIO с threading
"""
import multiprocessing

# Количество worker процессов
# Для SocketIO комнат нужно использовать 1 worker (комнаты хранятся в памяти)
workers = 1

# Worker класс для threading (лучше всего работает с Flask-SocketIO в threading режиме)
worker_class = 'sync'

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

# Threads для каждого worker (threading режим использует threads)
# Больше threads = больше одновременных соединений
threads = 4

