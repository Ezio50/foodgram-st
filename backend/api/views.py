from io import BytesIO
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from djoser.views import UserViewSet
from rest_framework import (
    viewsets,
    pagination,
    decorators,
    permissions,
    status,
    response
)
from api.serializers import (
    Ingredient_Serializer,
    Recipe_Serializer,
    Favorite_Serializer,
    Cart_Serializer,
    Author_Serializer,
    Create_User,
    Subscriber_Serializer,
    Subscription_Serializer
)
from api.permissions import Ownership_Permission
from recipe.models import Ingredient, Recipe, User_Cart


class Ingredient_Viewset(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = Ingredient_Serializer
    search_fields = ("^name",)
    pagination_class = pagination.PageNumberPagination
    permission_classes = (permissions.AllowAny,)


class Recipe_ViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = Recipe_Serializer
    pagination_class = pagination.PageNumberPagination
    permission_classes = (Ownership_Permission,)

    @decorators.action(
        detail=True,
        methods=("post", "delete"),
        url_path="favorite",
        url_name="favorite",
    )
    def favorite(self, request, pk):
        if request.method == "POST":
            return self.create_recipe_collection(
                request, pk, Favorite_Serializer
            )
        return self.delete_recipe_collection(
            request, pk, Favorite_Serializer.Meta.model.objects
        )

    @decorators.action(
        detail=True,
        methods=("post", "delete"),
        url_path="shopping_cart",
        url_name="shopping_cart",
    )
    def shopping_cart(self, request, pk):
        if request.method == "POST":
            return self.create_recipe_collection(
                request, pk, Cart_Serializer
            )
        return self.delete_recipe_collection(
            request, pk, Cart_Serializer.Meta.model.objects
        )

    def create_recipe_collection(self, request, pk, serializer_class):
        serializer = serializer_class(
            data={
                "user": request.user.id,
                "recipe": pk,
            }
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return response.Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe_collection(self, request, pk, queryset):
        queryset.get(user=request.user, recipe_id=pk).delete()

        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        detail=False,
        methods=("get",),
        url_path="download_shopping_cart",
        url_name="download_shopping_cart",
    )
    def download_shopping_cart(self, request):
        ingredients = (
            User_Cart.objects.filter(
                user=request.user
            )
            .values("recipe__ingredients__name", "recipe__ingredients__measurement_unit")
            .annotate(sum=Sum("recipe__ingredients__amount"))
        )

        return self.ingredients_to_txt(ingredients)

    def ingredients_to_txt(self, ingredients):
        shopping_list = "\n".join(
            f"{ingredient['ingredient_name']} - {ingredient['sum']} "
            f"({ingredient['ingredient__measurement_unit']})"
            for ingredient in ingredients
        )
        file = BytesIO()
        file.write(shopping_list)

        return FileResponse(
            file,
            as_attachment=True,
            filename="Список покупок.txt",
            content_type="text/plain"
        )

    @decorators.action(
        detail=True,
        methods=("get",),
        url_path="get-link",
        url_name="get-link",
    )
    def get_short_link(self, request, pk):
        instance = self.get_object()
        url = f"{request.get_host()}/s/{instance.id}"

        return response.Response(
            data={
                "short-link": url
            }
        )


class User_ViewSet(UserViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = Create_User
    pagination_class = pagination.PageNumberPagination

    @decorators.action(
        detail=False,
        methods=("get",),
        url_path="me",
        url_name="me",
    )
    def me(self, request):
        serializer = Author_Serializer(
            request.user, context={"request": request}
        )
        return response.Response(serializer.data)

    @decorators.action(
        detail=True,
        methods=("put", "delete"),
        url_path="avatar",
        url_name="avatar",
    )
    def avatar(self, request, id):
        if request.method == "PUT":
            return self.create_avatar(request)
        return self.delete_avatar(request)

    def create_avatar(self, request):
        serializer = Author_Serializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return response.Response(serializer.data)

    def delete_avatar(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete()
            user.avatar = None
            user.save()

        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        detail=False,
        methods=("get",),
        url_path="subscriptions",
        url_name="subscriptions",
    )
    def subscriptions(self, request):
        queryset = self.get_queryset().filter(
            subscriptions_where_subscribing_user=request.user
        )
        pages = self.paginate_queryset(queryset)
        serializer = Subscription_Serializer(
            pages, many=True, context={"request": request}
        )

        return self.get_paginated_response(serializer.data)

    @decorators.action(
        detail=True,
        methods=("post", "delete"),
        url_path="subscribe",
        url_name="subscribe",
    )
    def subscribe(self, request, id):
        if request.method == "POST":
            return self.create_subscription(request, id)
        return self.delete_subscription(request, id)

    def create_subscription(self, request, id):
        serializer = Subscription_Serializer(
            data={
                "subscriber": request.user.id,
                "target": id,
            },
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_serializer = Subscriber_Serializer(
            self.get_queryset().get(pk=id),
            context={"request": request}
        )

        return response.Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def delete_subscription(self, request, id):
        subscription = Subscription_Serializer.Meta.model.objects.get(
            subscribing_user=request.user.id, target=id
        )

        if not subscription.exists():
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()

        return response.Response(status=status.HTTP_204_NO_CONTENT)
