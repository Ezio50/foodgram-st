from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from foodgram import constants


class User(AbstractUser):

    email = models.EmailField(
        verbose_name="Электронная почта",
        max_length=constants.USER_EMAIL_LENGTH,
        unique=True,
    )
    username = models.CharField(
        verbose_name="Имя пользователя",
        max_length=constants.USER_CHAR_MAX_LENGTH,
        validators=[
            RegexValidator(regex=constants.USERNAME_REGEX)
        ],
        unique=True,
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=constants.USER_CHAR_MAX_LENGTH,
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=constants.USER_CHAR_MAX_LENGTH,
    )
    avatar = models.ImageField(
        verbose_name="Аватар",
        upload_to="user_pfp/",
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("-created_at",)

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    subscribing_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Субъект подписки",
    )
    target = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribers",
        verbose_name="Объект подписки",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=("subscribing_user", "target"),
                name="U_SUBSCRIPTIONS"
            )
        ]
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.subscribing_user} -> {self.target}"
