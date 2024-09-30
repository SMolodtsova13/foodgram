from django.db import transaction
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import exceptions, serializers

from api.core import Base64ImageFieldSerializer
from users.models import Follow
from recipes.models import (Favourites, Ingredient, Recipe,
                            Tag, IngredientRecipe, ShoppingList)


User = get_user_model()


class FoodgramUserSerializer(UserSerializer):
    """Получение списка пользователей и конкретного пользователя."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageFieldSerializer(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        """Проверка подписки пользователя"""
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and Follow.objects.filter(
                user=request.user, author=obj.id
            ).exists()
        )

    def validate(self, data):
        if 'avatar' not in data:
            raise serializers.ValidationError('Поле avatar обязательно!')
        return data

class FollowSerializer(serializers.ModelSerializer):
    """Подписки."""
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    avatar = Base64ImageFieldSerializer(source='author.avatar')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'id',
            'email',
            'avatar',
            'recipes',
            'username',
            'last_name',
            'first_name',
            'is_subscribed',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return ShortRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели Тег."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ингредиент."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientsRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор Ингредиенты в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CreateIngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания ингредиента в создании рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        write_only=True
    )

    @staticmethod
    def validate_amount(value):
        """Валидация количества ингредиентов."""
        if value < 1:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше 0!'
            )
        return value

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount',)


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов"""

    ingredients = CreateIngredientsInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageFieldSerializer(use_url=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def to_representation(self, instance):
        """Метод представления модели"""
        serializer = ReadRecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        )
        return serializer.data

    def validate(self, data):
        """Метод проверки данных"""
        tags = data.get('tags')

        if not tags:
            raise exceptions.ValidationError('Убедитесь, что добавлен тег!')
        if len(tags) > len(set(tags)):
            raise serializers.ValidationError(
                'Теги не должны повторяться!'
            )

        ingredients = data.get('ingredients')

        if not ingredients:
            raise exceptions.ValidationError(
                'Убедитесь, что добавлены ингредиенты!'
            )

        ids = [ing['id'] for ing in ingredients]

        if len(ids) > len(set(ids)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться!'
            )
        return data

    def __create_ingredients(self, ingredients, recipe):
        """Метод создания ингредиента"""
        ingredient_data = []
        for element in ingredients:
            id = element['id']
            amount = element['amount']
            ingredient_data.append(
                {'ingredient': id, 'recipe': recipe, 'amount': amount}
            )

        IngredientRecipe.objects.bulk_create(
            IngredientRecipe(**row) for row in ingredient_data
        )

    @transaction.atomic
    def __create_tags(self, tags, recipe):
        """Метод добавления тега"""
        recipe.tags.set(tags)

    @transaction.atomic
    def create(self, validated_data):
        """Метод создания модели"""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        request = self.context.get('request')
        recipe = Recipe.objects.create(
            author=request.user, **validated_data
        )

        self.__create_ingredients(ingredients, recipe)
        self.__create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Метод обновления модели"""
        instance.tags.clear()
        instance.ingredients.clear()

        self.__create_ingredients(validated_data.pop('ingredients'), instance)
        self.__create_tags(validated_data.pop('tags'), instance)

        return super().update(instance, validated_data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Дополнительный сериализатор для рецептов """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ReadRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели Рецепт."""

    author = FoodgramUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngredientsRecipeSerializer(source='ingredient_list',
                                              many=True,
                                              read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        """Проверка наличия рецепта в избранном."""
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and Favourites.objects.filter(
                user=request.user.id, recipe=obj.id
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """Проверка наличия рецепта в списке покупок."""
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and ShoppingList.objects.filter(
                user=request.user.id, recipe=obj.id
            ).exists()
        )
