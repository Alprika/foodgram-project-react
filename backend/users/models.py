from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Логин',
        max_length=50,
        unique=True,
        validators=(validate_username,),
        error_messages={'unique': 'Логин занят'}
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=100,
        unique=True,
        error_messages={'unique': 'Этот email уже зарегистрирован!'}
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=50,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=50,
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=50,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', 'password')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)
        constraints = (
            models.UniqueConstraint(
                fields=('email', 'username'),
                name='unique_username'
            ),
        )

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='subscribers',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор на которого подписались',
        on_delete=models.CASCADE,
        related_name='subscribed_authors',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author',),
                name='unique_subscription',),
            models.CheckConstraint(
                check=~models.Q(user=models.F("author")),
                name='self_following',
            ),
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
