from io import BytesIO

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework
from djoser import views
from rest_framework import (
    decorators,
    filters,
    permissions,
    response,
    status,
    viewsets
)

from api.filters import RecipeFilter
from api.permissions import OwnershipPermission, UserSelfPermission
from api.serializers import (
    CartSerializer,
    CreateAvatarSerializer,
    CreateRecipeSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    SubscriberSerializer,
    SubscriptionSerializer
)
from recipe.models import Ingredient, Recipe, UserCart


class IngredientViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("^name",)
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (OwnershipPermission,)
    filter_backends = (rest_framework.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ("create", "partial_update"):
            return CreateRecipeSerializer

        return RecipeSerializer

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
                request, pk, FavoriteSerializer
            )
        return self.delete_recipe_collection(
            request, pk, FavoriteSerializer.Meta.model.objects
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
                request, pk, CartSerializer
            )
        return self.delete_recipe_collection(
            request, pk, CartSerializer.Meta.model.objects
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
        return response.Response(status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(
        detail=False,
        methods=("get",),
        url_path="download_shopping_cart",
        url_name="download_shopping_cart",
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = UserCart.objects.filter(
            user=request.user
        ).values(
            "recipe__ingredients_in_recipe__ingredient__name",
            "recipe__ingredients_in_recipe__ingredient__measurement_unit"
        ).annotate(
            total=Sum('recipe__ingredients_in_recipe__amount')
        )

        return self.ingredients_to_txt(ingredients)

    def ingredients_to_txt(self, ingredients):
        shopping_list = []
        for ingredient in ingredients:
            name = ingredient[
                "recipe__ingredients_in_recipe__ingredient__name"
            ]
            unit = ingredient[
                "recipe__ingredients_in_recipe__ingredient__measurement_unit"
            ]
            total = ingredient["total"]
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


class UserViewSet(views.UserViewSet):
    queryset = get_user_model().objects.all()
    permission_classes = (UserSelfPermission,)

    @decorators.action(
        detail=True,
        methods=("put", "delete"),
        url_path="avatar",
        url_name="avatar",
        permission_classes=(permissions.IsAuthenticated,)
    )
    def avatar(self, request, id):
        if request.method == "PUT":
            return self.create_avatar(request)
        return self.delete_avatar(request)

    def create_avatar(self, request):
        serializer = CreateAvatarSerializer(
            request.user,
            data=request.data,
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
        serializer = SubscriberSerializer(
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
    def subscribe(self, request, id):
        get_object_or_404(
            get_user_model(),
            pk=id
        )
        if request.method == "POST":
            return self.create_subscription(request, id)
        return self.delete_subscription(request, id)

    def create_subscription(self, request, pk):
        if request.user.pk == int(pk):
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = SubscriptionSerializer(
            data={
                "subscribing_user": request.user.pk,
                "target": pk,
            },
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_serializer = SubscriberSerializer(
            self.get_queryset().get(pk=pk),
            context={"request": request}
        )

        return response.Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete_subscription(self, request, pk):
        queryset = SubscriptionSerializer.Meta.model.objects
        subscription = queryset.filter(
            subscribing_user=request.user, target_id=pk
        )
        if subscription.exists():
            subscription.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        return response.Response(status=status.HTTP_400_BAD_REQUEST)
