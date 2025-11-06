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
gunicorn main:application --bind 0.0.0.0:8000 --timeout 60 --worker-class gevent --workers 1 --worker-connections 1000
```

## Важные изменения:

1. ✅ Заменен `eventlet` на `gevent` - лучше работает с gunicorn
2. ✅ Создан `main.py` с экспортом `application` для gunicorn
3. ✅ Добавлен health check endpoint (`/` и `/health`)
4. ✅ Обновлены зависимости в `requirements.txt`

## Структура файлов:

```
backend/
├── app.py              # Основное приложение Flask с SocketIO
├── main.py             # Точка входа для gunicorn (экспортирует application)
├── requirements.txt    # Зависимости (включая gevent и gunicorn)
├── gunicorn_config.py  # Конфигурация gunicorn (опционально)
└── DEPLOY.md          # Подробная документация
```

## Проверка после деплоя:

1. Проверьте health check: `curl https://your-app-url/health`
2. Проверьте API: `curl https://your-app-url/api/users`
3. Проверьте WebSocket соединение через Socket.IO клиент

## Если возникают проблемы:

1. Убедитесь, что используется `--worker-class gevent`
2. Убедитесь, что используется `--workers 1` (не больше!)
3. Проверьте логи в панели Timeweb
4. Убедитесь, что порт 8000 доступен

## Переменные окружения:

Если нужно изменить порт:

```bash
PORT=8000
```

Но обычно Timeweb автоматически использует порт 8000.
