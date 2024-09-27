from django.urls import include, path, re_path
from rest_framework import routers

from api.views import (IngredientViewSet, TagViewSet,
                       RecipeViewSet, FoodgramUserViewSet)

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'users', FoodgramUserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]# path('auth/', include('djoser.urls')),
