from django.core.management.base import BaseCommand
from ingredients.models import Ingredient
import json
import os

class Command(BaseCommand):
    help = "Загрузка ингредиентов из JSON файла"

    def handle(self, *args, **kwargs):
        try:
            file_path = 'data/ingredients.json'
            if not os.path.exists(file_path):
                self.stdout.write(self.style.ERROR(f'Файл {file_path} не найден'))
                return

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                ingredient_count = 0

                for item in data:
                    Ingredient.objects.create(
                        name=item['name'],
                        measurement_unit=item['measurement_unit']
                    )
                    ingredient_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Импортировано {ingredient_count} ингредиентов'
                    )
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Ошибка: {e}'
                )
            )