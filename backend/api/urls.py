from django.urls import include, path, re_path
from rest_framework import routers

from api.views import (IngredientViewSet, TagViewSet,
                       RecipeViewSet, FoodgramUserViewSet)

app_name = 'api'

router = routers.DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register(r'users', FoodgramUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken'))
]
