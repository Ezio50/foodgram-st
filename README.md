# О проекте

Фудграм - платформа для распространения и управления рецептами.

# Технологии

- Django Rest Framework
- Gunicorn
- Postgres
- Nginx

# Как запустить

1. Создать и заполнить /backend/foodgram/.env файл с данными подключения к бд.
Например, .env файл может выглядеть так
```
NAME=foodgram
USER=foodgram_user
PASSWORD=password
HOST=postgres
PORT=5432
DEBUG=True
SECRET_KEY="your_secret_key"
ALLOWED_HOSTS="127.0.0.1 localhost"
CSRF_TRUSTED_ORIGINS="http://127.0.0.1 http://localhost"
```

2. Перейдите в директорию [/infra](/infra/) и запустите docker-compose проект. Сбор статики, миграции и наполнение бд тестовыми ингредиентами происходит **автоматически**. За автоматизацию отвечает command инструкция в файле [docker-compose.yml](infra/docker-compose.yml) (строка 20).
```
cd infra
docker compose up
```