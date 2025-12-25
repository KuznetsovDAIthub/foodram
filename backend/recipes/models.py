from django.contrib.auth import get_user_model
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models

from api.constants import (
    DEFAULT_VALUE,
    FIELD_LENGTH,
    MEASUREMENT_UNIT_LENGTH,
    VALIDATOR_MAX_VALUE,
    VALIDATOR_MIN_VALUE,
    COLOR_LENGTH,
)

User = get_user_model()


class Tag(models.Model):
    """Модель для тегов."""

    name = models.CharField(
        max_length=FIELD_LENGTH,
        unique=True,
        verbose_name='Тэг',
    )
    color = models.CharField(
        max_length=COLOR_LENGTH,
        unique=True,
        verbose_name=' Цвет',
    )
    slug = models.SlugField(
        max_length=FIELD_LENGTH,
        unique=True,
        verbose_name='Слаг тэга',
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = [
            'name',
        ]

    def __str__(self):
        """Строковое представление тега."""
        return self.name


class Ingredient(models.Model):
    """Модель для ингридиентов."""

    name = models.CharField(
        max_length=FIELD_LENGTH,
        verbose_name='Ингридиент',
    )
    measurement_unit = models.CharField(
        max_length=MEASUREMENT_UNIT_LENGTH,
        verbose_name='Единицы измерения',
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'], name='unique ingredient'
            )
        ]

    def __str__(self):
        """Строковое представление ингридиента."""
        return f"{self.name}, {self.measurement_unit}"


class Recipe(models.Model):
    """Модель для рецептов."""

    name = models.CharField(
        max_length=FIELD_LENGTH,
        verbose_name='Наименование',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='AmountIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    cooking_time = models.PositiveSmallIntegerField(
        default=DEFAULT_VALUE,
        verbose_name='Время приготовления',
        validators=(
            MinValueValidator(
                VALIDATOR_MIN_VALUE,
                'Укажите значение больше 0',
            ),
            MaxValueValidator(
                VALIDATOR_MAX_VALUE,
                'Укажите значение меньше 32000',
            ),
        ),
    )
    text = models.TextField(
        max_length=FIELD_LENGTH,
        verbose_name='Описание',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name='Дата публикации'
    )
    image = models.ImageField(
        upload_to='recipes/images',
        null=True,
        default=None,
        verbose_name='Изображение',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        """Строковое представление рецепта."""
        return f'Рецепт: {self.name}. Автор: {self.author.username}'


class AmountIngredient(models.Model):
    """Модель для связи рецептов и ингридиентов."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        default=DEFAULT_VALUE,
        verbose_name='Количество',
        validators=(
            MinValueValidator(
                VALIDATOR_MIN_VALUE,
                'Укажите значение больше 0',
            ),
            MaxValueValidator(
                VALIDATOR_MAX_VALUE,
                'Укажите значение меньше 32000',
            ),
        ),
    )

    class Meta:
        verbose_name = 'Количество'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ('recipe',)
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient',
            )
        ]

    def __str__(self):
        """Строковое представление количества ингредиентов."""
        return f'{self.amount} {self.ingredient}'


class Favorite(models.Model):
    """Модель для избранных рецептов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = [
            'recipe',
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='favorite recipe for user',
            )
        ]

    def __str__(self):
        """Строковое представление избранного."""
        return f'Пользователь: {self.user} Рецепт: {self.recipe}'


class ShoppingCart(models.Model):
    """Модель для корзины покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ['recipe']
        verbose_name = 'Корзина'
        verbose_name_plural = 'В корзине'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique cart for user',
            )
        ]

    def __str__(self):
        """Строковое представление корзины."""
        return f'Пользователь: {self.user} Рецепт: {self.recipe}'
