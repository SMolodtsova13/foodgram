from django.urls import include, path, re_path
from rest_framework import routers

from api.views import (IngredientViewSet, RecipeViewSet,
                       TagViewSet, UserViewSet)

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

v1_urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    re_path(r'auth/', include('djoser.urls.authtoken')),
]

urlpatterns = [
    path('api/', include(v1_urlpatterns)),
]

#     path('recipes/<int:id>/favorite/',
#          RecipeFavoritesViewSet.as_view(),
#          name='favorite',),
#     path('users/<int:id>/subscribe/',
#          FollowViewSet.as_view(),
#          name='subscribe',),
#     path('recipes/<int:id>/shopping_cart/',
#          ShoppingViewSet.as_view(),
#          name='shopping_cart',),

# if settings.DEBUG:
#     urlpatterns += static(
#         settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
#     )
