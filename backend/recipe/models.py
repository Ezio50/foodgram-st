from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models


class Ingredient(models.Model):
    name = models.CharField(
        max_length=128,
        verbose_name="Название",
    )
    measurement_unit = models.CharField(
        max_length=64,
        verbose_name="Единица измерения",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"], name="U_INGRIDIENT"
            )
        ]
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.name} - {self.measurement_unit}"


class Recipe(models.Model):
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="Ingredient_In_Recipe",
        verbose_name="Ингредиенты",
    )
    name = models.CharField(
        max_length=256,
        verbose_name="Название рецепта"
    )
    image = models.ImageField(
        upload_to="recipe_pic",
        verbose_name="Фотография",
    )
    text = models.TextField(
        verbose_name="Описание"
    )
    cooking_time = models.IntegerField(
        "Время приготовления (в минутах)",
        validators=[
            MinValueValidator(1),
        ],
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-created_at",)

    def __str__(self):
        return self.name


class Ingredient_In_Recipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipies",
        verbose_name="Ингредиент",
    )
    amount = models.IntegerField(
        verbose_name="Количество",
        validators=(
            MinValueValidator(1),
        ),
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "ingredient"),
                name="U_INGREDIENTS_IN_RECIPE"
            )
        ]

    def __str__(self):
        return f"{self.recipe} - {self.ingredient}"


class Recipe_collection_mixin(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="U_RECIPE_COLLECTION"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.recipe}"


class User_Favorite(Recipe_collection_mixin):

    class Meta:
        abstract = False
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        default_related_name = "favorites"


class User_Cart(Recipe_collection_mixin):

    class Meta:
        abstract = False
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        default_related_name = "in_cart"
