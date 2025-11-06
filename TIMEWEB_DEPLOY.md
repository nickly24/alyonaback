# Инструкция по деплою на Timeweb Cloud

## Настройки для Timeweb

### Тип приложения:

**Backend** (Flask)

### Команда сборки:

```bash
pip install -r requirements.txt
```

### Команда запуска:

```bash
gunicorn main:application --bind 0.0.0.0:8000 --timeout 60 --workers 1 --threads 4
```

**Важно:** Используем 1 worker с 4 threads для правильной работы SocketIO комнат (комнаты хранятся в памяти worker'а).

## Важные изменения:

1. ✅ Используется `threading` режим Flask-SocketIO - стабильно работает с gunicorn sync worker
2. ✅ Создан `main.py` с экспортом `application` для gunicorn
3. ✅ Добавлен health check endpoint (`/` и `/health`)
4. ✅ Обновлены зависимости в `requirements.txt` (удалены gevent, используется только threading)

## Структура файлов:

```
backend/
├── app.py              # Основное приложение Flask с SocketIO
├── main.py             # Точка входа для gunicorn (экспортирует application)
├── requirements.txt    # Зависимости (включая gunicorn, threading встроен в Python)
├── gunicorn_config.py  # Конфигурация gunicorn (опционально)
└── DEPLOY.md          # Подробная документация
```

## Проверка после деплоя:

1. Проверьте health check: `curl https://your-app-url/health`
2. Проверьте API: `curl https://your-app-url/api/users`
3. Проверьте WebSocket соединение через Socket.IO клиент

## Если возникают проблемы:

1. Убедитесь, что используется `--workers 1` (не больше!) для правильной работы SocketIO комнат
2. Убедитесь, что используется `--threads 4` для обработки нескольких соединений
3. Проверьте логи в панели Timeweb
4. Убедитесь, что порт 8000 доступен
5. Flask-SocketIO работает в `threading` режиме (указано в app.py)

## Переменные окружения:

Если нужно изменить порт:

```bash
PORT=8000
```

Но обычно Timeweb автоматически использует порт 8000.
