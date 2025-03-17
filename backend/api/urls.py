from django.urls import include, path
from rest_framework import routers

from api.views import User_ViewSet, Recipe_ViewSet, Ingredient_Viewset

router = routers.SimpleRouter()
router.register("ingredients", Ingredient_Viewset, basename="ingredients")
router.register("recipes", Recipe_ViewSet, basename="recipes")
router.register("users", User_ViewSet, basename="users")

app_name = "api"

urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
