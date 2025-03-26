from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from foodgram import constants


class Ingredient(models.Model):
    name = models.CharField(
        max_length=constants.INGREDIENT_NAME_LENGTH,
        verbose_name="Название",
    )
    measurement_unit = models.CharField(
        max_length=constants.MEASUREMENT_UNIT_LENGTH,
        verbose_name="Единица измерения",
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"], name="U_INGRIDIENT"
            )
        ]
        ordering = ("name",)

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
        through="IngredientInRecipe",
        verbose_name="Ингредиенты",
    )
    name = models.CharField(
        max_length=constants.RECIPE_NAME_LENGTH,
        verbose_name="Название рецепта"
    )
    image = models.ImageField(
        upload_to="recipe_pic",
        verbose_name="Фотография",
    )
    text = models.TextField(
        verbose_name="Описание"
    )
    cooking_time = models.PositiveIntegerField(
        "Время приготовления (в минутах)",
        validators=[
            MinValueValidator(constants.MIN_COOKING_TIME),
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


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredients_in_recipe",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент",
    )
    amount = models.PositiveIntegerField(
        verbose_name="Количество",
        validators=(
            MinValueValidator(constants.MIN_INGREDIENT_AMOUNT),
        ),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
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
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.recipe} - {self.ingredient}"


class RecipeCollectionMixin(models.Model):
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
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    class Meta:
        abstract = True
        unique_together = [
            ["user", "recipe"]
        ]
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user} - {self.recipe}"


class UserFavorite(RecipeCollectionMixin):

    class Meta(RecipeCollectionMixin.Meta):
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        default_related_name = "favorites"


class UserCart(RecipeCollectionMixin):

    class Meta(RecipeCollectionMixin.Meta):
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        default_related_name = "carts"
