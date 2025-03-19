from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from auth_user.models import Subscribe
from recipe.models import (
    Ingredient,
    Recipe,
    Ingredient_In_Recipe,
    User_Favorite,
    User_Cart,
)


class Ingredient_Serializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")
        read_only_fields = ("id", "name", "measurement_unit")


class Ingredient_Recipe_Serializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient_In_Recipe
        fields = ("id", "name", "measurement_unit", "amount")


class Author_Serializer(UserSerializer):
    avatar = Base64ImageField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "avatar",
            "is_subscribed"
        )

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user

        if not user.is_authenticated:
            return False

        return user.subscriptions.filter(
            target=obj.id
        ).exists()


class Create_Avatar_Serializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = get_user_model()
        fields = ("avatar",)

    def validate(self, attrs):
        if 'avatar' not in attrs:
            raise serializers.ValidationError(
                {"avatar": "Обязательное поле"}
            )

        return super().validate(attrs)


class Short_Recipe_Serializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class Recipe_Serializer(Short_Recipe_Serializer):
    author = Author_Serializer()
    ingredients = Ingredient_Recipe_Serializer(
        many=True,
        source="recipe_ingredients"
    )
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

        return request.user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")

        if not request.user.is_authenticated:
            return False

        return request.user.in_cart.filter(recipe=obj).exists()

    def create_ingredients(self, ingredient_list, recipe):
        Ingredient_In_Recipe.objects.bulk_create(
            Ingredient_In_Recipe(
                ingredient_id=i.get("ingredient").get("id"),
                recipe=recipe,
                amount=i.get("amount")
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
            "recipes", "recipes_count", "avatar"
        )

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes_limit = request.query_params.get("recipes_limit")
        if recipes_limit is None:
            recipes = obj.recipes.all()
        else:
            recipes = obj.recipes.all()[:int(recipes_limit)]

        return Short_Recipe_Serializer(
            recipes, context={"request": request}, many=True
        ).data


class Subscription_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = (
            "subscribing_user", "target"
        )


class Create_User(UserCreateSerializer):
    password = serializers.CharField(write_only=True)

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


class Recipe_Collection_Serializer(serializers.ModelSerializer):

    class Meta:
        abstract = True
        fields = ("user", "recipe")

    def to_representation(self, instance):
        serializer = Short_Recipe_Serializer(
            instance.recipe,
            context=self.context
        )
        return serializer.data

    def validate(self, attrs):
        queryset = self.Meta.model.objects
        user = attrs["user"]
        recipe = attrs["recipe"]

        if queryset.filter(
            recipe=recipe,
            user=user
        ).exists():
            raise serializers.ValidationError()

        return super().validate(attrs)


class Favorite_Serializer(Recipe_Collection_Serializer):
    class Meta:
        model = User_Favorite
        fields = ("user", "recipe")


class Cart_Serializer(Recipe_Collection_Serializer):
    class Meta:
        model = User_Cart
        fields = ("user", "recipe")


class Change_Password_Serializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user

        if user.check_password(attrs["current_password"]) or user.is_staff:
            return super().validate(attrs)
        else:
            raise serializers.ValidationError()


class Create_Ingredient_Serializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        fields = ("id", "amount")

    def validate_id(self, value):
        ingredient = Ingredient.objects.filter(pk=value)

        if not ingredient.exists():
            raise serializers.ValidationError()

        return value

    def validate_amount(self, value):
        if not value >= 1:
            raise serializers.ValidationError()

        return value


class Create_Recipe_Serializer(serializers.ModelSerializer):
    ingredients = Create_Ingredient_Serializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "ingredients",
            "name",
            "image",
            "name",
            "text",
            "cooking_time",
        )

    def validate(self, data):
        ingredients = data.get("ingredients")

        if not ingredients:
            raise serializers.ValidationError()

        ingredients_ids = [
            i["id"]
            for i in ingredients
        ]
        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise serializers.ValidationError()

        return data

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        user = self.context.get("request").user
        recipe = Recipe.objects.create(**validated_data, author=user)
        self.create_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        Ingredient_In_Recipe.objects.filter(recipe=instance).delete()
        self.create_ingredients(validated_data.pop("ingredients"), instance)

        return super().update(instance, validated_data)

    def create_ingredients(self, ingredients, recipe):
        Ingredient_In_Recipe.objects.bulk_create(
            Ingredient_In_Recipe(
                ingredient_id=i["id"],
                recipe=recipe,
                amount=i["amount"]
            )
            for i in ingredients
        )

    def to_representation(self, instance):
        serializer = Recipe_Serializer(
            instance,
            context={"request": self.context.get("request")}
        )
        return serializer.data
