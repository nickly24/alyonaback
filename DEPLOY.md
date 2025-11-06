# Инструкция по деплою на Timeweb

## Настройки для Timeweb Cloud

### Команда сборки:
```bash
pip install -r requirements.txt
```

### Команда запуска:
```bash
gunicorn main:application --bind 0.0.0.0:8000 --timeout 60 --worker-class eventlet --workers 1
```

Или используйте конфигурационный файл:
```bash
gunicorn main:application -c gunicorn_config.py
```

## Важные моменты:

1. **Worker класс**: Обязательно используйте `--worker-class eventlet` для Flask-SocketIO
2. **Количество workers**: Используйте `--workers 1` (один worker) для правильной работы SocketIO комнат
3. **Порт**: Timeweb использует порт 8000 по умолчанию
4. **Таймаут**: Установлен 60 секунд для WebSocket соединений

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

