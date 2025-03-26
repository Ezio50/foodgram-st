from json import loads

from django.conf import settings
from django.core.management.base import BaseCommand

from foodgram import constants
from recipe.models import Ingredient


class Command(BaseCommand):
    help = "Загрузка ингредиентов из JSON файла"

    def handle(self, *args, **kwargs):
        try:
            filename = settings.BASE_DIR / constants.INGREDIENT_FILE
            with open(filename, "r", encoding="utf-8") as file:
                ingredient_list = loads(file.read())

                for ingredient in ingredient_list:
                    Ingredient.objects.create(
                        name=ingredient["name"],
                        measurement_unit=ingredient["measurement_unit"]
                    )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Импортировано {len(ingredient_list)} ингридиентов"
                    )
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Ошибка: {e}"
                )
            )
