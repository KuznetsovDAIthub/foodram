from django.contrib import admin

from .models import (
    AmountIngredient,
    Ingredient,
    Recipe,
    Tag,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка для тегов."""

    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для ингредиентов."""

    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка для рецептов."""

    list_display = ('name', 'author', 'cooking_time')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)


@admin.register(AmountIngredient)
class AmountIngredientAdmin(admin.ModelAdmin):
    """Админка для количества ингредиентов."""

    list_display = ('recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')
