from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):

    email = models.EmailField(
        verbose_name="Электронная почта",
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        verbose_name="Имя пользователя",
        max_length=150,
        validators=[
            RegexValidator(regex=r"^[\w.@+-]+\Z")
        ],
        unique=True,
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=150,
    )
    avatar = models.ImageField(
        verbose_name="Аватар",
        upload_to="user_pfp/",
        blank=True,
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

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

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=("subscribing_user", "target"),
                name="U_SUBSCRIPTIONS"
            )
        ]

    def __str__(self):
        return f"{self.subscribing_user} -> {self.target}"
