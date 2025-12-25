from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import (
    UniqueTogetherValidator,
)

from recipes.models import (
    AmountIngredient,
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
)
from api.constants import (
    DEFAULT_VALUE,
    VALIDATOR_MAX_VALUE,
    VALIDATOR_MIN_VALUE,
)
from users.models import MyUser, Subscriptions


class MyUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""

    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = MyUser
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
            'avatar',
        )


class MyUserSerializer(UserSerializer):
    """Сериализатор для отображения пользователя."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = MyUser
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        ]

    def get_is_subscribed(self, obj):
        """Проверка, подписан ли пользователь на автора."""
        if not hasattr(obj, 'subscribers'):
            return False
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.subscribers.filter(user=request.user).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class AmountIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели AmountIngredient."""

    id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField()
    amount = serializers.IntegerField(
        default=DEFAULT_VALUE,
        validators=[
            MinValueValidator(
                VALIDATOR_MIN_VALUE,
                'Количество должно быть больше 0',
            ),
            MaxValueValidator(
                VALIDATOR_MAX_VALUE,
                'Количество должно быть меньше 32000',
            ),
        ],
    )

    class Meta:
        model = AmountIngredient
        fields = ['id', 'name', 'amount', 'measurement_unit']

    def to_representation(self, instance):
        """Преобразование ингредиента в сериализованный вид."""
        return {
            'id': instance.ingredient.id,
            'name': instance.ingredient.name,
            'amount': instance.amount,
            'measurement_unit': instance.ingredient.measurement_unit,
        }


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""

    tags = TagSerializer(many=True, read_only=True)
    author = MyUserSerializer(read_only=True)
    ingredients = AmountIngredientSerializer(
        many=True,
        source='recipe',
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorite'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        ]

    def get_is_favorite(self, obj):
        """Получение информации о том, является ли рецепт избранным."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        """Получение информации о том, находится ли рецепт в корзине."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.cart.filter(user=request.user).exists()


class AddIngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиента в рецепт."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = AmountIngredient
        fields = ['id', 'amount']


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    author = MyUserSerializer(read_only=True)
    ingredients = AddIngredientRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        default=DEFAULT_VALUE,
        validators=[
            MinValueValidator(
                VALIDATOR_MIN_VALUE,
                'Время приготовления должно быть больше 0',
            ),
            MaxValueValidator(
                VALIDATOR_MAX_VALUE,
                'Время приготовления должно быть меньше 32000',
            ),
        ],
    )

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        ]

    def validate(self, data):
        """Валидация данных для создания рецепта."""
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Добавьте хотя бы один ингредиент'}
            )
        ingredient_ids = [ingredient.get('id') for ingredient in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {'ingredients': 'Ингредиенты должны быть уникальными'}
            )
        return data

    def create_ingredients(self, recipe, ingredients):
        """Создание связей с ингредиентами."""
        amount_ingredients = [
            AmountIngredient(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount'],
            ) for ingredient in ingredients
        ]
        AmountIngredient.objects.bulk_create(amount_ingredients)

    def create(self, validated_data):
        """Создание рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта."""
        if 'ingredients' in self.initial_data:
            ingredients = self.initial_data.get('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(instance, ingredients)
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            instance.tags.set(tags)
        validated_data.pop('ingredients', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Преобразование рецепта в сериализованный вид."""
        return RecipeSerializer(instance, context=self.context).data


class ShowFavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения избранного."""

    class Meta:
        model = Favorite
        fields = ['id', 'name', 'image', 'cooking_time']


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для корзины покупок."""

    class Meta:
        model = ShoppingCart
        fields = ['user', 'recipe']

    def to_representation(self, instance):
        """Преобразование корзины покупок в сериализованный вид."""
        return RecipeSerializer(instance.recipe, context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного."""

    class Meta:
        model = Favorite
        fields = ['user', 'recipe']

    def to_representation(self, instance):
        """Преобразование избранного в сериализованный вид."""
        return RecipeSerializer(instance.recipe, context=self.context).data


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    class Meta:
        model = Subscriptions
        fields = ['user', 'author']
        validators = [
            UniqueTogetherValidator(
                queryset=Subscriptions.objects.all(),
                fields=['user', 'author'],
                message='Вы уже подписаны на этого автора',
            )
        ]

    def to_representation(self, instance):
        """Преобразование подписки в сериализованный вид."""
        return MyUserSerializer(instance.author, context=self.context).data


class ShowSubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения подписок."""

    email = serializers.EmailField(source='author.email')
    id = serializers.IntegerField(source='author.id')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Subscriptions
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        ]

    def get_recipes(self, obj):
        """Получение рецептов для подписки."""
        request = self.context['request']
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.author.recipes.all()
        if recipes_limit:
            recipes = recipes[: int(recipes_limit)]
        return RecipeSerializer(recipes, many=True, context=self.context).data

    def get_recipes_count(self, obj):
        """Получение количества рецептов для подписки."""
        return obj.author.recipes.count()

    def get_is_subscribed(self, obj):
        """Получение информации о том, подписан ли пользователь на автора."""
        return True


pattern = r'''
.* город.? (?P<city>[а-яА-я]+) .*? улиц.? (?P<street>[а-яА-я]+) .*? дом.? (?P<number>\d+) .*? квартир.? (?P<flat>\d+)[.,]?
'''

pattern = r'''
.* город.? (?P<city>[а-яА-я]+) .*? улиц.? (?P<street>[а-яА-я]+) .*? дом.? (?P<number>\d+) .*? квартир.? (?P<flat>\d+)
'''

for address in addresses:
    match = re.search(pattern, address)
    if match:
        print(match.groupdict())
