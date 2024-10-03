from django.db.models import Sum
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.serializers import (FavouritesSerializer, FollowCreateSerializer,
                             IngredientSerializer, FollowSerializer,
                             ReadRecipeSerializer, ShoppingListSerializer,
                             TagSerializer, CreateRecipeSerializer,
                             UserAvatarSerializer)
from api.permissions import IsAuthorOrReadOnlyPermission
from recipes.models import (IngredientRecipe, Tag, Ingredient, Favourites,
                            Recipe, ShoppingList)
from users.models import Follow

User = get_user_model()


class FoodgramUserViewSet(UserViewSet):
    """Вьюсет пользователя."""

    pagination_class = LimitOffsetPagination

    def get_permissions(self):
        if self.action == 'me':
            return (IsAuthenticated(),)
        return super().get_permissions()

    @action(detail=False,
            methods=('PUT', 'DELETE',),
            url_path='me/avatar',
            permission_classes=(IsAuthenticated,))
    def avatar(self, request):
        """Добавление/удаление аватара."""
        user = self.request.user
        if request.method == 'PUT':
            serializer = UserAvatarSerializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {'avatar': request.build_absolute_uri(user.avatar.url)},
                status=status.HTTP_200_OK
            )

        self.request.user.avatar = None
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=('GET',),
            url_path='subscriptions',
            url_name='subscriptions')
    def subscriptions(self, request):
        """Просмотр подписок пользователя."""
        queryset = User.objects.filter(follower__user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request, 'user': request.user}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=('POST', 'DELETE',),
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id=None):
        """Подписка на автора."""
        user = request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            folow_data = {'user': user.id, 'author': int(id)}
            serializer = FollowCreateSerializer(
                data=folow_data,
                context={'request': request, 'user': user})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                data=serializer.data, status=status.HTTP_201_CREATED
            )
        delete_count, _ = Follow.objects.filter(
            user=user, author=author
        ).delete()
        if delete_count == 0:
            return Response({'errors': 'Вы уже отписались!'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FoodgramReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    """ReadOnly model viewset with presets."""

    permission_classes = (AllowAny,)
    pagination_class = None


class TagViewSet(FoodgramReadOnlyModelViewSet):
    """Получение списка тегов, конкретного тега."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(FoodgramReadOnlyModelViewSet):
    """Получение списка ингредиентов, конкретного ингредиента."""

    permission_classes = (IsAuthorOrReadOnlyPermission,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для управления рецептами."""
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnlyPermission,)

    def get_serializer_class(self):
        """Метод для вызова определенного сериализатора."""
        if self.action in ('create', 'partial_update'):
            return CreateRecipeSerializer
        return ReadRecipeSerializer

    @action(methods=('GET',), detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        """Получение короткой ссылки на рецепт."""
        recipe = self.get_object()
        short_link = request.build_absolute_uri(f'/{recipe.short_url}')
        data = {'short-link': short_link}
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=('POST', 'DELETE',),
            detail=True,
            permission_classes=(IsAuthenticated,),
            url_name='shopping_cart',
            url_path='shopping_cart')
    def add_shopping_item(self, request, pk=None):
        """Добавление/удаление рецепта из списка покупок."""
        get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return self.__create_obj_recipes(
                ShoppingListSerializer, request, pk
            )
        return self.__delete_obj_recipes(request, ShoppingList, pk)

    @action(methods=('GET',),
            detail=False,
            permission_classes=(IsAuthenticated,),
            url_path='download_shopping_cart',
            url_name='download_shopping_cart')
    def download_shopping_list(self, request):
        """Загрузка списка покупок."""
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_recipe__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).order_by('ingredient__name').annotate(sum=Sum('amount'))
        result = ''
        for ingredient in ingredients:
            result += (
                f"{ingredient['ingredient__name']}  - "
                f"{ingredient['sum']}"
                f"({ingredient['ingredient__measurement_unit']})\n"
            )
        response = HttpResponse(result, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    @action(methods=('POST', 'DELETE'),
            detail=True,
            permission_classes=(IsAuthenticated,),
            url_path='favorite',
            url_name='favorite')
    def favorite(self, request, pk=None):
        """Добавление/удаление рецепта в избранное."""
        get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return self.__create_obj_recipes(
                FavouritesSerializer, request, pk
            )
        return self.__delete_obj_recipes(request, Favourites, pk)

    def __create_obj_recipes(self, serializer, request, pk):
        """Добавить рецепт."""
        data = {'user': request.user.id, 'recipe': int(pk)}
        serializer_obj = serializer(data=data)
        serializer_obj.is_valid(raise_exception=True)
        serializer_obj.save()
        return Response(serializer_obj.data, status=status.HTTP_201_CREATED)

    def __delete_obj_recipes(self, request, model, pk):
        """Удалить рецепт."""
        delete_count, _ = model.objects.filter(
            user=request.user, recipe__id=pk
        ).delete()
        if delete_count == 0:
            return Response({'errors': 'Рецепт уже удален'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)
