from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from recipes.models import Recipe, Tag, RecipeIngredient
from ingredients.models import Ingredient
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class Command(BaseCommand):
    help = 'Добавляет тестовые данные: пользователей, теги и рецепты'

    def handle(self, *args, **kwargs):
        # Создание пользователей
        users = [
            {'email': 'user1@example.com', 'username': 'user1', 'first_name': 'User', 'last_name': 'One', 'password': 'password123'},
            {'email': 'user2@example.com', 'username': 'user2', 'first_name': 'User', 'last_name': 'Two', 'password': 'password123'},
        ]
        for user_data in users:
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                username=user_data['username'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Создан пользователь: {user.username}'))

        # Создание тегов
        tags = [
            {'name': 'Завтрак', 'color': '#FF0000', 'slug': 'breakfast'},
            {'name': 'Обед', 'color': '#00FF00', 'slug': 'lunch'},
        ]
        for tag_data in tags:
            tag, created = Tag.objects.get_or_create(**tag_data)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создан тег: {tag.name}'))

        # Создание рецептов
        ingredient = Ingredient.objects.first()
        if not ingredient:
            self.stdout.write(self.style.ERROR('Нет ингредиентов в базе. Сначала выполните load_ingredients.'))
            return

        for user in User.objects.all():
            recipe, created = Recipe.objects.get_or_create(
                author=user,
                name=f'Рецепт от {user.username}',
                description='Тестовый рецепт',
                cooking_time=30,
                image=SimpleUploadedFile('test.jpg', b'file_content', content_type='image/jpeg')
            )
            if created:
                recipe.tags.add(Tag.objects.first())
                RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, amount=100)
                self.stdout.write(self.style.SUCCESS(f'Создан рецепт: {recipe.name}'))

        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно добавлены'))