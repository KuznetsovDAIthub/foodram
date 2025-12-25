from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from api.constants import FIELD_LENGTH


class MyUser(AbstractUser):
    """Модель для пользователей."""

    email = models.EmailField(
        max_length=FIELD_LENGTH,
        unique=True,
        verbose_name='Адрес электронной почты',
        error_messages={
            'unique': 'Пользователь с таким email уже существует.'
        },
    )
    username = models.CharField(
        max_length=FIELD_LENGTH,
        unique=True,
        verbose_name='Имя пользователя',
        error_messages={
            'unique': 'Пользователь с таким именем уже существует.'
        },
    )
    first_name = models.CharField(
        max_length=FIELD_LENGTH,
        verbose_name='Имя',
        blank=False,
    )
    last_name = models.CharField(
        max_length=FIELD_LENGTH,
        verbose_name='Фамилия',
        blank=False,
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='Аватар',
        default=None,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        """Строковое представление пользователя."""
        return self.username


class Subscriptions(models.Model):
    """Модель для подписок на авторов рецептов."""

    author = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='subscribers',
        help_text='Автор, на которого подписываются',
    )
    user = models.ForeignKey(
        MyUser,
        verbose_name='Подписчики',
        on_delete=models.CASCADE,
        related_name='subscriptions',
        help_text='Пользователь, который подписывается',
    )
    subscribed_at = models.DateTimeField(
        verbose_name='Дата подписки',
        auto_now_add=True,
        editable=False,
        help_text='Дата и время создания подписки',
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = 'Подписки'
        unique_together = ('author', 'user')
        ordering = ['-subscribed_at']

    def clean(self):
        """Проверка, что пользователь не может подписаться на самого себя."""
        if self.author == self.user:
            raise ValidationError(
                'Пользователь не может подписаться на самого себя.'
            )

    def __str__(self):
        """Строковое представление подписки."""
        return f'{self.user} подписан на {self.author}'
