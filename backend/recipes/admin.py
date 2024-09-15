from django.contrib import admin

from recipes.models import (Tag, Ingredient, Favourites, Recipe,
                            IngredientRecipe, TagRecipe, ShoppingList)


# @admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    list_filter = ('color',)
    empty_value_display = 'Поле не заполнено'


# @admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'unit_of_measurement')
    list_filter = ('name',)
    empty_value_display = 'Поле не заполнено'


# @admin.register(IngredientRecipe)
class IngredientsInLine(admin.StackedInline):
    model = IngredientRecipe
    extra = 1


# @admin.register(TagRecipe)
class TagsInLine(admin.StackedInline):
    model = TagRecipe
    extra = 1


# @admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'pub_date', 'text')
    search_fields = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    inlines = (IngredientsInLine, TagsInLine)
    empty_value_display = 'Поле не заполнено'


# @admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'volume',)
    empty_value_display = 'Поле не заполнено'


# @admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'tag',)
    empty_value_display = 'Поле не заполнено'


# @admin.register(Favourites)
class FavouritesRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    empty_value_display = 'Поле не заполнено'


# @admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    empty_value_display = 'Поле не заполнено'


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
# admin.site.register(IngredientRecipe, RecipeIngredientAdmin)
# admin.site.register(TagRecipe, RecipeIngredientAdmin)
admin.site.register(Favourites, FavouritesRecipeAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
