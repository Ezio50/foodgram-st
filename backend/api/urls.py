from django.urls import include, path
from rest_framework import routers

from api.views import UserViewSet, RecipeViewSet, IngredientViewset

router = routers.SimpleRouter()
router.register("ingredients", IngredientViewset, basename="ingredients")
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("users", UserViewSet, basename="users")

app_name = "api"

urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
