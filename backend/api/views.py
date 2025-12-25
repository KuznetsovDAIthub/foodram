from io import BytesIO

import base64
from django.core.files.base import ContentFile
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrAdminOrReadOnly
from api.serializers import (
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    ShowSubscriptionsSerializer,
    SubscriptionSerializer,
    TagSerializer,
    MyUserSerializer,
)
from api.constants import (
    FONT_NAME,
    FONT_SIZE,
    FONT_SIZE_SMALL,
    PAGE_INGREDIENT_X,
    PAGE_INGREDIENT_Y,
    PAGE_INGREDIENT_Y_STEP,
    PAGE_MARGIN,
    PAGE_TITLE_X,
    PAGE_TITLE_Y,
)
from recipes.models import (
    AmountIngredient,
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.models import MyUser, Subscriptions

pdfmetrics.registerFont(TTFont(FONT_NAME, 'DejaVuSans.ttf'))


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для добавления/изменения/удаления/просмотра рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    search_fields = ['name', 'author__username']

    def get_serializer_context(self):
        """Добавляет request в контекст сериализатора."""
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def get_serializer_class(self):
        """Возвращает класс сериализатора в зависимости от типа запроса."""
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=['get'])
    def get_link(self, request, pk=None):
        """Получение короткой ссылки на рецепт."""
        recipe = self.get_object()
        full_url = request.build_absolute_uri(f'/recipes/{recipe.id}/')
        return Response({'short-link': full_url})


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для отображения ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для отображения тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class ShoppingCartViewSet(APIView):
    """Добавление и удаление рецепта из корзины покупок."""

    permission_classes = [IsAuthenticated]

    def post(self, request, recipe_id):
        """Добавление рецепта в корзину покупок."""
        recipe = get_object_or_404(Recipe, id=recipe_id)
        shopping_cart, created = ShoppingCart.objects.get_or_create(
            user=request.user, recipe=recipe
        )
        if not created:
            return Response(
                {'errors': 'Рецепт уже в корзине'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ShoppingCartSerializer(shopping_cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        """Удаление рецепта из корзины покупок."""
        recipe = get_object_or_404(Recipe, id=recipe_id)
        shopping_cart = get_object_or_404(
            ShoppingCart, user=request.user, recipe=recipe
        )
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get(self, request):
        """Скачивание списка покупок в формате PDF."""
        recipes = Recipe.objects.filter(cart__user=request.user)
        ingredients = (
            AmountIngredient.objects.filter(recipe__in=recipes)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )

        if not ingredients:
            return Response(
                {'errors': 'Список покупок пуст'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)

        p.setFont(FONT_NAME, FONT_SIZE)

        p.drawString(PAGE_TITLE_X, PAGE_TITLE_Y, 'Список покупок')
        p.setFont(FONT_NAME, FONT_SIZE_SMALL)

        y = PAGE_INGREDIENT_Y
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['total_amount']
            text = f'{name} ({unit}) - {amount}'
            p.drawString(PAGE_INGREDIENT_X, y, text)
            y -= PAGE_INGREDIENT_Y_STEP
            if y < PAGE_MARGIN:
                p.showPage()
                y = PAGE_INGREDIENT_Y
                p.setFont(FONT_NAME, FONT_SIZE_SMALL)

        p.save()

        pdf = buffer.getvalue()
        buffer.close()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="shopping-list.pdf"'
        )
        return response


class FavoriteViewSet(APIView):
    """Добавление и удаление рецепта из избранного."""

    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def post(self, request, recipe_id):
        """Добавление рецепта в избранное."""
        recipe = get_object_or_404(Recipe, id=recipe_id)
        favorite, created = Favorite.objects.get_or_create(
            user=request.user, recipe=recipe
        )
        if not created:
            return Response(
                {'errors': 'Рецепт уже в избранном'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = RecipeSerializer(recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        """Удаление рецепта из избранного."""
        recipe = get_object_or_404(Recipe, id=recipe_id)
        try:
            favorite = Favorite.objects.get(user=request.user, recipe=recipe)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Favorite.DoesNotExist:
            return Response(
                {'errors': 'Рецепт не был в избранном'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class SubscriptionViewSet(APIView):
    """Добавление и удаление подписки на пользователя."""

    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def post(self, request, user_id):
        """Подписка на пользователя."""
        author = get_object_or_404(MyUser, id=user_id)
        subscription, created = Subscriptions.objects.get_or_create(
            user=request.user, author=author
        )
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        """Отписка от пользователя."""
        author = get_object_or_404(MyUser, id=user_id)
        subscription = get_object_or_404(
            Subscriptions, user=request.user, author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShowSubscriptionsViewSet(ListAPIView):
    """Отображение подписок пользователя."""

    serializer_class = ShowSubscriptionsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        """Получение списка подписок текущего пользователя."""
        return self.request.user.subscriptions.select_related("author")

    def get_serializer_context(self):
        """Добавление recipes_limit в контекст сериализатора."""
        context = super().get_serializer_context()
        context['recipes_limit'] = self.request.query_params.get(
            'recipes_limit'
        )
        return context


class UserAvatarViewSet(viewsets.ModelViewSet):
    """ViewSet для обновления аватара пользователя."""

    permission_classes = [IsAuthenticated]
    serializer_class = MyUserSerializer
    http_method_names = ['post', 'patch', 'put', 'delete']

    def get_object(self):
        """Получение текущего пользователя."""
        return self.request.user

    def put(self, request, *args, **kwargs):
        """Обновление аватара пользователя."""
        return self._handle_avatar(request)

    def post(self, request, *args, **kwargs):
        """Добавление аватара пользователя."""
        return self._handle_avatar(request)

    def patch(self, request, *args, **kwargs):
        """Обновление аватара пользователя."""
        return self._handle_avatar(request)

    def delete(self, request, *args, **kwargs):
        """Удаление аватара пользователя."""
        user = self.get_object()
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _handle_avatar(self, request):
        """Обработка загрузки аватара."""
        user = self.get_object()

        if "avatar" not in request.data:
            return Response(
                {'error': 'Аватар не найден в запросе'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            avatar_data = request.data['avatar']
            if isinstance(avatar_data, str) and avatar_data.startswith(
                'data:image'
            ):
                format, imgstr = avatar_data.split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(
                    base64.b64decode(imgstr),
                    name=f'avatar.{ext}',
                )
                user.avatar = data
                user.save()

                serializer = self.get_serializer(user)
                return Response(serializer.data)
            else:
                return Response(
                    {'error': 'Неверный формат данных аватара'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {'error': f'Ошибка при сохранении аватара: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
