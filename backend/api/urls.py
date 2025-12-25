from django.urls import include, path
from rest_framework import routers

from api.views import (
    FavoriteViewSet,
    IngredientViewSet,
    RecipeViewSet,
    ShoppingCartViewSet,
    ShowSubscriptionsViewSet,
    SubscriptionViewSet,
    TagViewSet,
    UserAvatarViewSet,
)

app_name = 'api'

router = routers.DefaultRouter()

router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')


urlpatterns = [
    path(
        'recipes/<int:pk>/get-link/',
        RecipeViewSet.as_view({'get': 'get_link'}),
        name='recipe-get-link',
    ),
    path(
        'recipes/download_shopping_cart/',
        ShoppingCartViewSet.as_view(),
        name='download_shopping_cart',
    ),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        ShoppingCartViewSet.as_view(),
        name='shopping_cart',
    ),
    path(
        'recipes/<int:recipe_id>/favorite/',
        FavoriteViewSet.as_view(),
        name='favorite',
    ),
    path(
        'users/<int:user_id>/subscribe/',
        SubscriptionViewSet.as_view(),
        name='subscribe',
    ),
    path(
        'users/subscriptions/',
        ShowSubscriptionsViewSet.as_view(),
        name='subscriptions',
    ),
    path(
        'users/me/avatar/',
        UserAvatarViewSet.as_view({
            'put': 'put',
            'post': 'post',
            'patch': 'patch',
            'delete': 'delete',
        }),
        name='user_avatar',
    ),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    path('', include(router.urls)),
]
