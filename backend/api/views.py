from io import BytesIO
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework
from rest_framework import (
    viewsets,
    decorators,
    permissions,
    status,
    response,
    filters
)
from api.serializers import (
    Ingredient_Serializer,
    Recipe_Serializer,
    Favorite_Serializer,
    Cart_Serializer,
    Author_Serializer,
    Create_User,
    Subscriber_Serializer,
    Subscription_Serializer,
    Create_Avatar_Serializer,
    Change_Password_Serializer,
    Create_Recipe_Serializer
)
from api.permissions import Ownership_Permission, Auth_RO_Staff
from api.filters import Recipe_Filter
from recipe.models import Ingredient, Recipe, User_Cart


class Ingredient_Viewset(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = Ingredient_Serializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("^name",)
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class Recipe_ViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (Ownership_Permission,)
    filter_backends = (rest_framework.DjangoFilterBackend,)
    filterset_class = Recipe_Filter

    def get_serializer_class(self):
        if self.action in ("create", "partial_update"):
            return Create_Recipe_Serializer

        return Recipe_Serializer

    @decorators.action(
        detail=True,
        methods=("post", "delete"),
        url_path="favorite",
        url_name="favorite",
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, pk):
        get_object_or_404(
            Recipe,
            pk=pk
        )

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
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        get_object_or_404(
            Recipe,
            pk=pk
        )

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

        return response.Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete_recipe_collection(self, request, pk, queryset):
        recipe = queryset.filter(user=request.user, recipe_id=pk)
        if recipe.exists():
            recipe.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(
        detail=False,
        methods=("get",),
        url_path="download_shopping_cart",
        url_name="download_shopping_cart",
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = User_Cart.objects.filter(
            user=request.user
        ).values(
            "recipe__recipe_ingredients__ingredient__name",
            "recipe__recipe_ingredients__ingredient__measurement_unit"
        ).annotate(
            total=Sum('recipe__recipe_ingredients__amount')
        )

        return self.ingredients_to_txt(ingredients)

    def ingredients_to_txt(self, ingredients):
        shopping_list = []
        for i in ingredients:
            name = i["recipe__recipe_ingredients__ingredient__name"]
            unit = i[
                "recipe__recipe_ingredients__ingredient__measurement_unit"
            ]
            total = i["total"]
            shopping_list.append(f"{name} - {total}({unit})")
        shopping_list_str = "\n".join(shopping_list)
        file = BytesIO()
        file.write(shopping_list_str.encode())
        file.seek(0)

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
        url = f"{request.get_host()}/s/{instance.pk}"

        return response.Response(
            data={
                "short-link": url
            }
        )


class User_ViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = Create_User
    permission_classes = (Auth_RO_Staff,)

    def get_serializer_class(self):
        if self.action in ("create", "partial_update"):
            return Create_User

        return Author_Serializer

    @decorators.action(
        detail=False,
        methods=("get",),
        url_path="me",
        url_name="me",
        permission_classes=(permissions.IsAuthenticated,)
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
        permission_classes=(permissions.IsAuthenticated,)
    )
    def avatar(self, request, pk):
        if request.method == "PUT":
            return self.create_avatar(request)
        return self.delete_avatar(request)

    def create_avatar(self, request):
        serializer = Create_Avatar_Serializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return response.Response(
            serializer.data
        )

    def delete_avatar(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete()
            user.avatar = None
            user.save()

        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        detail=False,
        methods=("post",),
        url_path="set_password",
        url_name="set_password",
        permission_classes=(permissions.IsAuthenticated,)
    )
    def set_password(self, request):
        serializer = Change_Password_Serializer(
            data=request.data,
            context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            new_password = serializer.data["new_password"]
            request.user.set_password(new_password)
            request.user.save()

            return response.Response(status=status.HTTP_204_NO_CONTENT)

        return response.Response(status=status.HTTP_401_UNAUTHORIZED)

    @decorators.action(
        detail=False,
        methods=("get",),
        url_path="subscriptions",
        url_name="subscriptions",
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscriptions(self, request):
        targets = request.user.subscriptions.values("target")
        queryset = self.get_queryset().filter(
            pk__in=targets
        )
        pages = self.paginate_queryset(queryset)
        serializer = Subscriber_Serializer(
            pages, many=True, context={"request": request}
        )

        return self.get_paginated_response(serializer.data)

    @decorators.action(
        detail=True,
        methods=("post", "delete"),
        url_path="subscribe",
        url_name="subscribe",
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, pk):
        get_object_or_404(
            get_user_model(),
            pk=pk
        )
        if request.method == "POST":
            return self.create_subscription(request, pk)
        return self.delete_subscription(request, pk)

    def create_subscription(self, request, pk):
        if request.user.pk == int(pk):
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = Subscription_Serializer(
            data={
                "subscribing_user": request.user.pk,
                "target": pk,
            },
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_serializer = Subscriber_Serializer(
            self.get_queryset().get(pk=pk),
            context={"request": request}
        )

        return response.Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete_subscription(self, request, pk):
        queryset = Subscription_Serializer.Meta.model.objects
        subscription = queryset.filter(
            subscribing_user=request.user, target_id=pk
        )
        if subscription.exists():
            subscription.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
