from django.contrib import admin

from recipes.models import (Tag, Ingredient, Favourites, Recipe,
                            IngredientRecipe, TagRecipe, ShoppingList)


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    empty_value_display = 'Поле не заполнено'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)
    empty_value_display = 'Поле не заполнено'


class IngredientsInLine(admin.StackedInline):
    model = IngredientRecipe
    extra = 1


class TagsInLine(admin.StackedInline):
    model = TagRecipe
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'pub_date', 'text')
    search_fields = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    inlines = (IngredientsInLine, TagsInLine)
    empty_value_display = 'Поле не заполнено'


class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount',)
    empty_value_display = 'Поле не заполнено'


class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'tag',)
    empty_value_display = 'Поле не заполнено'


class FavouritesRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    empty_value_display = 'Поле не заполнено'


class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    empty_value_display = 'Поле не заполнено'


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favourites, FavouritesRecipeAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
