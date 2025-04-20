# О проекте

Фудграм - платформа для распространения и управления рецептами.

# Как запустить

1. Клонируйте репозиторий:

```
git clone https://github.com/Ezio50/foodgram-st.git 
cd foodgram-st
```
1. Создать и заполнить /backend/foodgram/.env файл с данными подключения к бд.
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

2. Перейдите в директорию [/infra](/infra/) и запустите docker-compose проект. Сбор статики, миграции и наполнение бд тестовыми ингредиентами происходит автоматически.
```
cd infra
docker compose up
```
3. Откройте сайт в браузере: **http://localhost**