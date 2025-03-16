from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from recipe.models import (Ingredient, Recipe, Ingredient_In_Recipe)


class Ingredient_Serializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")
        read_only_fields = ("id", "name", "measurement_unit")


class Ingredient_Recipe_Serializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient_In_Recipe
        fields = ("id", "name", "measurement_unit", "amount")


class Author_Serializer():
    avatar = Base64ImageField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ("id", "email", "username", "first_name", "last_name")


class Recipe_Serializer(serializers.ModelSerializer):
    author = Author_Serializer()
    ingredients = Ingredient_Serializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        request = self.context.get("request")

        if not request.user.is_authenticated:
            return False

        return request.user.favorites.filter(pk=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")

        if not request.user.is_authenticated:
            return False

        return request.user.in_cart.filter(pk=obj.id).exists()

    def create_ingredients(self, ingredient_list, recipe):
        Ingredient_In_Recipe.objects.bulk_create(
            Ingredient_In_Recipe(
                ingredient_id=i.get("id"),
                recipe=recipe,
                amount = i.get("amount")
            )
            for i in ingredient_list
        )
    
    def create(self, validated_data):
        # Removes ingredients to not conflict with recipe creation
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context.get("request").user
        )
        self.create_ingredients(
            ingredients,
            recipe
        )

        return recipe

    def update(self, instance, validated_data):
        # Update through recreation
        Ingredient_In_Recipe.objects.filter(
            recipe=instance.id
        ).delete()
        self.create_ingredients(
            validated_data.pop("ingredients"),
            instance
        )

        return super().update(instance, validated_data)
    

class Subscriber_Serializer(Author_Serializer):
    recipes = serializers.SerializerMethodField(method_name="get_recipes")
    recipes_count = serializers.IntegerField(source="recipes.count")

    class Meta:
        model = get_user_model()
        fields = (
            "id", "email", "username", "first_name", "last_name",
            "recipes", "recipes_count"
        )

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes_limit = request.query_params.get("recipes_limit")
        recipes = obj.recipes.all()[:int(recipes_limit)]

        return Recipe_Serializer(
            recipes, context={"request": request}, many=True
        )
    

class Create_User(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )


class Avatar_Serializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = get_user_model()
        fields = ("avatar",)
