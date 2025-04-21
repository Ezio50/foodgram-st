FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем содержимое папки backend
COPY . /app/

# Запускаем миграции, загрузку данных и Gunicorn
CMD ["sh", "-c", "python manage.py migrate && python manage.py load_ingredients && python manage.py add_test_data && python manage.py collectstatic --noinput && gunicorn backend.wsgi:application --bind 0.0.0.0:8000"]