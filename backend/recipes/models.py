from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from recipes.constants import (MAX_LENGTH_RECIPES_UNIT_MEASUREMENT,
                               MIN_VALUE, NAME_MAX_LENGTH_RECIPES)

User = get_user_model()


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField('Название тега',
                            max_length=NAME_MAX_LENGTH_RECIPES,
                            unique=True)
    color = ColorField('Цвет в HEX', default='#008000')
    slug = models.SlugField('Уникальный слаг тега',
                            max_length=NAME_MAX_LENGTH_RECIPES,
                            unique=True)

    class Meta:
        ordering = ('id',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name[:50]


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField('Название ингредиента',
                            max_length=NAME_MAX_LENGTH_RECIPES)
    measurement_unit = models.CharField(
        'Единица измерения', max_length=MAX_LENGTH_RECIPES_UNIT_MEASUREMENT
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name="unique_ingredient",
            ),
        )

    def __str__(self):
        return self.name[:50]


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        through_fields=('recipe', 'ingredient'),
        related_name="recipes",
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(Tag,
                                  through='TagRecipe',
                                  through_fields=('recipe', 'tag'))
    name = models.CharField('Название рецепта',
                            max_length=NAME_MAX_LENGTH_RECIPES)
    pub_date = models.DateTimeField('Дата публикации рецепта',
                                    auto_now_add=True)
    text = models.TextField('Описание рецепта',
                            help_text='Заполните описание рецепта')
    cooking_time = models.IntegerField(
        'Время приготовления в минутах',
        validators=(MinValueValidator(MIN_VALUE),)
    )
    image = models.ImageField('Изображение для рецепта',
                              upload_to='recipes/')
    
    short_url = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Модель для связи рецепта и ингредиентов"""

    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='ingredient_list',
                               verbose_name='Рецепт')
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   verbose_name='Ингредиент')
    amount = models.IntegerField(verbose_name='Количество ингридиентов',
                                 validators=(MinValueValidator(MIN_VALUE),))

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = (models.UniqueConstraint(
            fields=('ingredient', 'recipe', 'amount'),
            name='unique_ingredient_recipe_combination'
        ),)

    def __str__(self):
        return self.ingredient


class TagRecipe(models.Model):
    """Модель тегов в рецепте."""

    recipe = models.ForeignKey(Recipe,
                               verbose_name='Рецепт',
                               on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag,
                            verbose_name='Тег',
                            on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Теги'
        verbose_name_plural = 'Теги'
        constraints = (models.UniqueConstraint(
            fields=('tag', 'recipe'), name='unique_tag_recipe_combination'
        ),)

    def __str__(self):
        return f'{self.tag} {self.recipe}'


class Favourites(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_favorite_recipe'
            ),
        )

    def __str__(self):
        return f'Рецепт {self.recipe} в избранном у {self.user.username}'


class ShoppingList(models.Model):
    """Список покупок."""

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        constraints = (models.UniqueConstraint(
            fields=('user', 'recipe'), name='unique_shopping_list_recipe'
        ),)

        constraints = (models.UniqueConstraint(
            fields=('user', 'recipe'), name='unique_shopping_list'
        ),)

    def __str__(self):
        return f'Рецепт {self.recipe} в списке покупок {self.user.username}'
