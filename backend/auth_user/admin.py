from django.contrib import admin
from auth_user.models import Subscribe, User


@admin.register(User)
class User_Admin(admin.ModelAdmin):
    list_display = (
        "pk",
        "email",
        "username",
        "first_name",
        "last_name",
        "avatar"
    )
    search_fields = ("email", "username")


@admin.register(Subscribe)
class Subscription_Admin(admin.ModelAdmin):
    list_display = ("pk", "subscribing_user", "target")
    search_fields = (
        "subscribing_user__username",
        "target__username",
        "subscribing_user__email",
        "target__email"
    )
