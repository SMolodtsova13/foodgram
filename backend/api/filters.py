from django.contrib.auth import get_user_model
from django_filters import filters
from django_filters.rest_framework import FilterSet

from recipes.models import Recipe, Tag

User = get_user_model()


class RecipeFilter(FilterSet):
    """Фильтр для отображения избранного и списка покупок."""
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    is_favorited = filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(method='filter_in_shopping_list')

    def filter_is_favorited(self, queryset, name, value):
        if value == 1:
            user = self.request.user
            print(str(queryset))
            return queryset.filter(favorites__user_id=user.id)
        return queryset

    def filter_in_shopping_list(self, queryset, name, value):
        if value == 1:
            user = self.request.user
            print(str(queryset))
            return queryset.filter(shopping_recipe__user_id=user.id)
        return queryset

    class Meta: 
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')
