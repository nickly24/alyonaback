# Инструкция по деплою на Timeweb

## Настройки для Timeweb Cloud

### Команда сборки:
```bash
pip install -r requirements.txt
```

### Команда запуска:
```bash
gunicorn main:application --bind 0.0.0.0:8000 --timeout 60 --workers 1 --threads 4
```

**Важно:** Используем 1 worker с 4 threads для правильной работы SocketIO комнат (комнаты хранятся в памяти worker'а).

Или используйте конфигурационный файл:
```bash
gunicorn main:application -c gunicorn_config.py
```

## Важные моменты:

1. **Worker класс**: Используется `sync` worker (по умолчанию) с threading режимом Flask-SocketIO
2. **Количество workers**: Используется 1 worker для правильной работы SocketIO комнат (комнаты хранятся в памяти)
3. **Threads**: `--threads 4` позволяет обрабатывать несколько запросов одновременно в worker'е
4. **Порт**: Timeweb использует порт 8000 по умолчанию
5. **Таймаут**: Установлен 60 секунд для WebSocket соединений
6. **Режим SocketIO**: Используется `threading` режим, который стабильно работает с gunicorn

## Переменные окружения:

Если нужно изменить порт, используйте переменную окружения:
```bash
PORT=8000
```

## Проверка работоспособности:

После деплоя проверьте:
1. HTTP запросы: `curl http://your-app-url:8000/api/users`
2. WebSocket соединение через Socket.IO клиент

## Альтернативный запуск (если gunicorn не работает):

Если gunicorn вызывает проблемы, можно использовать прямое запуск через socketio:
```python
# В main.py изменить на:
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8000))
    socketio.run(app, debug=False, host='0.0.0.0', port=port)
```

Но Timeweb обычно требует gunicorn для production.

