# О проекте

Фудграм - платформа для распространения и управления рецептами. Пользователи могут публиковать рецепты, добавлять прочие
рецепты в избранное, собирать списки покупок и подписываться на других авторов.

# Технологии

- Django Rest Framework
- Djoser
- Gunicorn
- Postgres
- Nginx

# Как запустить

1. Создать и заполнить /backend/foodgram/.env файл с данными подключения к бд. Пример необходимых полей представлен в файле [.env.example](/backend/foodgram/.env.example). Убедитесь, что данные совместимы с настройкой бд в [docker-compose.yml](/infra/docker-compose.yml).

Например, .env файл может выглядеть так
```
NAME=foodgram
USER=foodgram_u
PASSWORD=1eHPdAi918Lf7X6b
HOST=postgres
PORT=5432
DEBUG=True
SECRET_KEY="django-insecure-@q*c2bpx_qnq4f$fhi40x0(^mqo@$ao#fq4cgi5q6^7_nxuu4^"
ALLOWED_HOSTS="127.0.0.1 localhost"
CSRF_TRUSTED_ORIGINS="http://127.0.0.1 http://localhost"
```

2. Перейдите в директорию [/infra](/infra/) и запустите docker-compose проект. Сбор статики, миграции и наполнение бд тестовыми ингредиентами происходит **автоматически**. За автоматизацию отвечает command инструкция в файле [docker-compose.yml](infra/docker-compose.yml) (строка 20).
```
cd infra
docker compose up
```
