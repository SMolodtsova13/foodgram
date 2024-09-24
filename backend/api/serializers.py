import base64
from sqids import Sqids

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import exceptions, serializers
from rest_framework.validators import UniqueTogetherValidator

from users.validators import validate_username, validate_email
from users.models import Follow
from recipes.models import (Tag, Favourites, Ingredient, Recipe,
                            IngredientRecipe, ShoppingList, TagRecipe)


User = get_user_model()


class Base64ImageFieldSerializer(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserValidationMixin:
    """Миксин для валидации username и  email пользователя."""

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
        fields = ('id',
                  'email',
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
    avatar = Base64ImageFieldSerializer(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('id',
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'avatar')

    def get_is_subscribed(self, obj):
        """Проверка подписки пользователя"""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()


class FollowSerializer(CustomUserSerializer):
    """Подписки."""
    recipes_count = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_recipes_count'
    )
    recipes = serializers.SerializerMethodField(read_only=True,
                                                method_name='get_recipes')

    class Meta:
        model = User
        fields = ('id',
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'avatar',
                  'recipes',
                  'recipes_count')

    def get_recipes(self, obj):
        """Метод для получения рецептов"""
        request = self.context.get('request')
        all_recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            all_recipes = all_recipes[:int(recipes_limit)]
        return ShortRecipeSerializer(all_recipes, many=True).data

    def get_recipes_count(self, obj):
        print("get_recipes_count")
        """Количество рецептов автора."""
        return obj.recipes.count()


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
        validators = UniqueTogetherValidator(
            queryset=IngredientRecipe.objects.all(), fields=('ingredient',
                                                             'recipe'),
        )


class CreateIngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания ингредиента в создании рецепта."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

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
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов"""

    ingredients = CreateIngredientsInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageFieldSerializer(use_url=True)

    class Meta:
        model = Recipe
        fields = ('ingredients',
                  'tags',
                  'name',
                  'image',
                  'text',
                  'cooking_time')
        
    def to_representation(self, instance):
        """Метод представления модели"""

        serializer = RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        )
        return serializer.data

    def __check_lists(self, list1, list2, message):
        for el in list1:
            if el not in list2:
                raise serializers.ValidationError(
                    message
                )

    def validate(self, data):
        """Метод проверки данных"""

        if not self.initial_data.get('tags'):
            raise exceptions.ValidationError('Убедитесь, что добавлен тег!')
        
        tag_ids = [tag for tag in self.initial_data.get('tags')]

        if len(tag_ids) > len(set(tag_ids)):
            raise serializers.ValidationError(
                'Теги не должны повторяться!'
            )

        all_tags = [tag.id for tag in Tag.objects.all()]
        self.__check_lists(tag_ids, all_tags, 'Тегов не существует!')
        
        if not self.initial_data.get('ingredients'):
            raise exceptions.ValidationError(
                'Убедитесь, что добавлены ингредиенты!'
            )
        
        ids = [ing['id'] for ing in self.initial_data.get('ingredients')]
        
        if len(ids) > len(set(ids)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться!'
            )
        
        all_ingredients = [ing.id for ing in Ingredient.objects.all()]
        self.__check_lists(ids, all_ingredients, 'Ингредиентов не существует!')

        return data

    def __create_ingredients(self, ingredients, recipe):
        """Метод создания ингредиента"""

        for element in ingredients:
            id = element['id']
            amount = element['amount']           

            ingredient = Ingredient.objects.get(pk=id)
            IngredientRecipe.objects.create(
                ingredient=ingredient,
                recipe=recipe,
                amount=amount
            )

    def __create_tags(self, tags, recipe):
        """Метод добавления тега"""
        recipe.tags.set(tags)

    def create(self, validated_data):
        """Метод создания модели"""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        keys_for_short_url = [recipe.id, len(ingredients), recipe.cooking_time]
        sqids = Sqids()
        code = sqids.encode(keys_for_short_url)
        recipe.short_url = code
        recipe.save()

        self.__create_ingredients(ingredients, recipe)
        self.__create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Метод обновления модели"""
        IngredientRecipe.objects.filter(recipe=instance).delete()
        TagRecipe.objects.filter(recipe=instance).delete()

        self.__create_ingredients(validated_data.pop('ingredients'), instance)
        self.__create_tags(validated_data.pop('tags'), instance)

        return super().update(instance, validated_data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Дополнительный сериализатор для рецептов """

    class Meta:
        """Мета-параметры сериализатора"""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели Рецепт."""

    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngredientsRecipeSerializer(source='ingredient_list',
                                              many=True,
                                              read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'name',
                  'image',
                  'text',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'cooking_time')

    def get_is_favorited(self, obj):
        """Проверка наличия рецепта в избранном."""
        user_id = self.context.get('request').user.id
        return Favourites.objects.filter(user=user_id, recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверка наличия рецепта в списке покупок."""
        user_id = self.context.get('request').user.id
        return ShoppingList.objects.filter(user=user_id,
                                           recipe=obj.id).exists()


class FavoritesSerializer(serializers.ModelSerializer):
    """"Сериализатор модели Избранное."""

    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')
    image = Base64ImageFieldSerializer(source='recipe.image', read_only=True)

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
    image = Base64ImageFieldSerializer(source='recipe.image', read_only=True)
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
