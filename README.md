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
HOST=localhost
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

3. Также, подготовку системы к работе можно провести вручную:
    1. Изменить [docker-compose.yml](infra/docker-compose.yml) файл (строка 20), чтобы убрать автоматизацию.
    ```
    + command: gunicorn foodgram.wsgi:application --bind 0:8000
    ```
    2. Запустить контейнеры
    ```
    cd infra
    docker compose up
    ```
    3. Собрать статику
    ```
    docker compose exec backend python manage.py collectstatic --noinput
    ```
    4. Создать миграции
    ```
    docker compose exec backend python manage.py makemigrations
    ```
    5. Выполнить миграции
    ```
    docker compose exec backend python manage.py migrate
    ```
    6. Импортировать ингредиенты
    ```
    docker compose exec backend python manage.py parse_ingredients
    ```

# Примеры запросов

## 1. Список избраных рецептов
```
req:
GET /api/recipes/?is_favorited=1

resp:
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 7,
            "author": {
                "id": 8,
                "email": "ddd@ddd.ddd",
                "username": "Пользователь3",
                "first_name": "Имя 3",
                "last_name": "Фамилия 3",
                "avatar": null,
                "is_subscribed": false
            },
            "ingredients": [
                {
                    "id": 1039,
                    "name": "молоко 6%",
                    "measurement_unit": "мл",
                    "amount": 200
                },
                {
                    "id": 1839,
                    "name": "тесто слоеное",
                    "measurement_unit": "г",
                    "amount": 5
                },
                {
                    "id": 1946,
                    "name": "филе лосося",
                    "measurement_unit": "г",
                    "amount": 500
                }
            ],
            "is_favorited": true,
            "is_in_shopping_cart": false,
            "name": "Бред",
            "image": "http://localhost:8000/media/recipe_pic/neochoue_BOqeHyq.jpg",
            "text": "Бредовая смесь бреда.",
            "cooking_time": 1000
        },
        {
            "id": 5,
            "author": {
                "id": 7,
                "email": "ccc@bbb.bbb",
                "username": "Пользователь4",
                "first_name": "Имя 4",
                "last_name": "Фамилия 4",
                "avatar": "http://localhost:8000/media/user_pfp/4bcfc8d6-14db-4983-b78e-2467d3c26b82.jpg",
                "is_subscribed": false
            },
            "ingredients": [
                {
                    "id": 2180,
                    "name": "яйца куриные",
                    "measurement_unit": "г",
                    "amount": 200
                },
                {
                    "id": 472,
                    "name": "индейка тушка",
                    "measurement_unit": "шт.",
                    "amount": 1
                },
                {
                    "id": 1188,
                    "name": "пагр",
                    "measurement_unit": "г",
                    "amount": 5000
                }
            ],
            "is_favorited": true,
            "is_in_shopping_cart": false,
            "name": "Симулятор",
            "image": "http://localhost:8000/media/recipe_pic/5372237b-dd4a-47c1-a7af-5cc2b154cf05.jpg",
            "text": "Необычно",
            "cooking_time": 20
        }
    ]
}
```

## 2. Добавление рецепта в список покупок
```
req:
POST /api/recipes/5/shopping_cart/

resp:
{
    "id": 5,
    "name": "Симулятор",
    "image": "http://localhost:8000/media/recipe_pic/5372237b-dd4a-47c1-a7af-5cc2b154cf05.jpg",
    "cooking_time": 20
}
```

## 3. Создание рецепта
```
req:
POST /api/recipes/

{
    "ingredients": [
        {
            "id": 1123,
            "amount": 10
        }
    ],
    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
    "name": "string",
    "text": "string",
    "cooking_time": 1
}

resp:
{
    "id": 8,
    "author": {
        "id": 6,
        "email": "bbb@bbb.bbb",
        "username": "Пользователь34",
        "first_name": "Имя 34",
        "last_name": "Фамилия 34",
        "avatar": "http://localhost:8000/media/user_pfp/4bcfc8d6-14db-4983-b78e-2467d3c26b82.jpg",
        "is_subscribed": false
    },
    "ingredients": [
        {
            "id": 1123,
            "name": "овощи",
            "measurement_unit": "г",
            "amount": 10
        }
    ],
    "is_favorited": false,
    "is_in_shopping_cart": false,
    "name": "string",
    "image": "http://localhost:8000/media/recipe_pic/7f743fac-bf8b-450d-abe7-e445411d5961.png",
    "text": "string",
    "cooking_time": 1
}
```

# Автор

Зайда Артур
