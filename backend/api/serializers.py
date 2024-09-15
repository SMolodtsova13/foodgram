from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import exceptions, serializers
from rest_framework.validators import UniqueTogetherValidator
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField

from users.validators import validate_username, validate_email
from users.models import Follow
from recipes.models import (Tag, Favourites, Ingredient,
                            Recipe, IngredientRecipe, ShoppingList)

User = get_user_model()


class UserValidationMixin:

    def validate_username(self, value):
        return validate_username(value)

    def validate_email(self, value):
        return validate_email(value)


class CustomUserCreateSerializer(UserCreateSerializer, UserValidationMixin):
    """Создание пользователя foodgram."""

    email = serializers.EmailField()
    username = serializers.CharField()

    class Meta:
        model = User
        fields = ('email',
                  'username',
                  'first_name',
                  'last_name',
                  'password')

    def validate(self, user_data):
        email = user_data.get('email')
        username = user_data.get('username')

        if User.objects.filter(email=email).exists():
            if User.objects.filter(username=username).exists():
                return user_data
            raise ValidationError(f'Email {email} уже существует')

        if User.objects.filter(username=username).exists():
            raise ValidationError(f'Username {username} уже существует')
        return user_data


class CustomUserSerializer(UserSerializer):
    """Получение списка пользователей и конкретного пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id',
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',)

    def get_is_subscribed(self, obj):
        """Проверка подписки пользователя"""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()


class FollowSerializer(serializers.ModelSerializer):
    """Подписки."""

    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True,
                                                source='author.recipes')

    class Meta:
        model = Follow
        fields = ('id',
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count')

    def get_is_subscribed(self, obj):
        """Проверка подписки пользователя на автора."""
        return Follow.objects.filter(user=obj.user, author=obj.author).exists()

    def get_recipes_count(self, obj):
        """Количество рецептов автора."""
        return Recipe.objects.filter(author=obj.author).count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели Тег."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ингредиент."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'unit_of_measurement')


class IngredientsRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор Ингредиенты в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    unit_of_measurement = serializers.ReadOnlyField(
        source='ingredient.unit_of_measurement'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'unit_of_measurement', 'volume')
        validators = UniqueTogetherValidator(
            queryset=IngredientRecipe.objects.all(), fields=('ingredient',
                                                             'recipes'),
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели Рецепт."""

    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    in_shopping_list = serializers.SerializerMethodField()
    image = Base64ImageField(source='recipe.image', read_only=True)

    class Meta:
        model = Recipe
        exclude = ('pub_date',)
        read_only_fields = ('author', 'tags',)

    def get_is_favorited(self, obj):
        """Проверка наличия рецепта в избранном."""
        user_id = self.context.get('request').user.id
        return Favourites.objects.filter(user=user_id, recipe=obj.id).exists()

    def get_in_shopping_list(self, obj):
        """Проверка наличия рецепта в списке покупок."""
        user_id = self.context.get('request').user.id
        return ShoppingList.objects.filter(user=user_id,
                                           recipe=obj.id).exists()

    def validate_tags(self, value):
        """Метод валидации тега при создании рецепта."""
        if not value:
            raise exceptions.ValidationError('Убедитесь, что добавлен тег!')
        return value

    def validate_ingredients(self, value):
        """Метод валидации ингридиентов при создании рецепта."""
        if not value:
            raise exceptions.ValidationError(
                'Убедитесь, что добавлены ингредиенты!'
            )
        ingredients = (item('id') for item in value)
        for ingredient in ingredients:
            if ingredients.count(ingredient) > 1:
                raise exceptions.ValidationError(
                    'В рецепте не может быть два одинаковых ингридиентов!'
                )
        return value

    def create(self, validated_data):
        """Создание рецепта."""
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта"""

        if 'ingredients' in validated_data:
            ingredients = validated_data['ingredients']
            instance.ingredients.clear()
            instance.ingredients.set(ingredients)
        if 'tags' in validated_data:
            tags_data = validated_data['tags']
            instance.tags.set(tags_data)
        return super().update(instance, validated_data)


class FavoritesSerializer(serializers.ModelSerializer):
    """"Сериализатор модели Избранное."""

    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')
    image = Base64ImageField(source='recipe.image', read_only=True)

    class Meta:
        model = Favourites
        fields = ('id', 'name', 'image', 'cooking_time')
        validators = UniqueTogetherValidator(
            queryset=Favourites.objects.all(), fields=('user', 'recipes'),
        )

    def validate(self, user_data):
        """Валидация при добавлении рецепта в избранное."""
        user = user_data.get('user')
        recipe = user_data.get('recipe')
        if Favourites.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(f'Рецепт {recipe} уже добавлен в избранное!')
        return user_data


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор модели Список Покупок."""
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = ShoppingList
        fields = ('id', 'name', 'image', 'cooking_time')
        validators = UniqueTogetherValidator(
            queryset=ShoppingList.objects.all(), fields=('user', 'recipes'),
        )

    def validate(self, user_data):
        """Валидация при добавлении рецепта в список покупок."""
        user = user_data.get('user')
        recipe = user_data.get('recipe')

        if ShoppingList.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(f'Рецепт {recipe} уже добавлен в список!')
        return user_data
