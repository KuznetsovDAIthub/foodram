from django_filters import rest_framework

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(rest_framework.FilterSet):
    """Фильтр для рецептов."""

    author = rest_framework.CharFilter()
    tags = rest_framework.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = rest_framework.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        """Фильтр для избранных рецептов."""
        if not hasattr(self.request, 'user') or not (
            self.request.user.is_authenticated
        ):
            return queryset.none()
        return queryset.filter(
            favorites__user=self.request.user) if value else queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтр для списка покупок."""
        if not hasattr(self.request, 'user') or not (
            self.request.user.is_authenticated
        ):
            return queryset.none()
        return queryset.filter(
            cart__user=self.request.user) if value else queryset


class IngredientFilter(rest_framework.FilterSet):
    """Фильтр для ингредиентов."""

    name = rest_framework.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Поиск по названию ингредиента',
    )

    class Meta:
        model = Ingredient
        fields = ['name']
