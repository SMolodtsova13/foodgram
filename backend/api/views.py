from django.db.models import Sum
from django.contrib.auth import get_user_model
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets, serializers
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.serializers import (IngredientSerializer, FollowSerializer,
                             RecipeSerializer, CustomUserSerializer,
                             FavoritesSerializer, ShoppingListSerializer,
                             TagSerializer, CreateRecipeSerializer)
from api.permissions import IsAuthorOrReadOnlyPermission
from api.pagination import LimitPagination
from recipes.models import (IngredientRecipe, Tag, Ingredient, Favourites,
                            Recipe, ShoppingList)
from users.models import Follow

User = get_user_model()


class FoodgramUserViewSet(UserViewSet):
    """Вьюсет пользователя."""

    pagination_class = LimitOffsetPagination

    @action(detail=False,
            methods=('PUT', 'DELETE',),
            url_path='me/avatar',
            permission_classes=(IsAuthenticated,))
    def avatar(self, request):
        """Добавление/удаление аватара."""
        user = self.request.user
        if request.method == 'PUT':
            serializer = CustomUserSerializer(user,
                                              data=request.data,
                                              partial=True)
            if 'avatar' not in request.data:
                return Response({'avatar': ['Это поле обязательно.']},
                                status=status.HTTP_400_BAD_REQUEST)
            if not serializer.is_valid():
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(
                {'avatar': request.build_absolute_uri(user.avatar.url)},
                status=status.HTTP_200_OK
            )
        elif request.method == 'DELETE':
            self.request.user.avatar = None
            self.request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=('GET',),
            url_path='subscriptions',
            url_name='subscriptions')
    def subscriptions(self, request):
        """Просмотр подписок пользователя."""
        user = self.request.user
        queryset = [f.author for f in Follow.objects.filter(user=user)]
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(pages,
                                      many=True,
                                      context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=('POST', 'DELETE',))
    def subscribe(self, request, id=None):
        """Подписка на автора."""
        user = self.request.user
        author = get_object_or_404(User, id=id)

        if user == author:
            return Response(
                {'errors': 'Нельзя подписаться/отписаться от себя!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            if Follow.objects.filter(user=user, author=author).exists():
                return Response({'errors': 'Подписка уже оформлена!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if request.method == 'POST':
                follow = Follow.objects.create(author=author, user=user)
                serializer = FollowSerializer(follow.author,
                                              context={'request': request})
                return Response(data=serializer.data,
                                status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not Follow.objects.filter(user=user, author=author).exists():
                return Response({'errors': 'Вы уже отписались!'},
                                status=status.HTTP_400_BAD_REQUEST)
            subscription = get_object_or_404(Follow, user=user, author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class FollowViewSet(viewsets.ModelViewSet):
    """Операции над подписками пользователей."""

    serializer_class = FollowSerializer
    pagination_class = LimitPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    @action(methods=('POST',), detail=True)
    def follow(self, request, pk=None):
        """Подписка на автора."""
        author = get_object_or_404(User, id=pk)
        follow = Follow.objects.create(user=request.user, author=author)
        serializer = FollowSerializer(follow, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=('DELETE',), detail=True)
    def unfollow(self, request, pk=None):
        """Отмена подписки на автора."""
        author = get_object_or_404(User, id=pk)
        Follow.objects.filter(user=request.user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=('GET',))
    def subscribers(self, request):
        """Список всех авторов, на которых подписан пользователь."""
        user = self.request.user
        queryset = Follow.objects.filter(user=user).values_list('author',
                                                                flat=True)
        authors = User.objects.filter(id__in=queryset)
        serializer = CustomUserSerializer(authors, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=('GET',))
    def subscribed_by(self, request):
        """Список пользователей, подписанных на текущего автора."""
        author = self.request.user
        queryset = Follow.objects.filter(author=author).values_list('user',
                                                                    flat=True)
        users = User.objects.filter(id__in=queryset)
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)


class CustomReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    """ReadOnly model viewset with presets."""

    permission_classes = (AllowAny,)
    pagination_class = None
    http_method_names = ('get',)


class TagViewSet(CustomReadOnlyModelViewSet):
    """Получение списка тегов, конкретного тега."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(CustomReadOnlyModelViewSet):
    """Получение списка ингредиентов, конкретного ингредиента."""

    permission_classes = (IsAuthorOrReadOnlyPermission,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('^name',)


def redirect_to_full_recipe(request, short_url):
    recipe = get_object_or_404(Recipe, short_url=short_url)
    full_url = f'/recipes/{recipe.id}'
    return HttpResponseRedirect(full_url)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для управления рецептами."""
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnlyPermission,)

    def get_serializer_class(self):
        """Метод для вызова определенного сериализатора. """

        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        elif self.action in ('create', 'partial_update'):
            return CreateRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=('DELETE',),
            detail=True,
            permission_classes=(IsAuthorOrReadOnlyPermission,))
    def delete_recipe(self, request, pk=None):
        try:
            recipe = self.get_object()
        except Recipe.DoesNotExist:
            raise Http404
        if request.user != recipe.author:
            return Response({'error': 'Вы не можете удалить данный рецепт.'},
                            status=status.HTTP_403_FORBIDDEN)
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
        try:
            recipe = Recipe.objects.get(id=pk)
        except Recipe.DoesNotExist:
            raise Http404

        if request.method == 'POST':
            if ShoppingList.objects.filter(user=request.user,
                                           recipe=recipe).exists():
                raise serializers.ValidationError(
                    'Невозможно повторно добавить рецепт в корзину!'
                )
            shopping_list = ShoppingList.objects.create(user=request.user,
                                                        recipe=recipe)
            serializer = ShoppingListSerializer(shopping_list)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            delete_recipe, _ = ShoppingList.objects.filter(
                user=request.user, recipe=recipe
            ).delete()
            if not delete_recipe:
                raise serializers.ValidationError(
                    'Невозможно удалить рецепт из корзины, которого нет!'
                )
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('GET',),
            detail=False,
            permission_classes=(IsAuthenticated,),
            url_path='download_shopping_cart',
            url_name='download_shopping_cart')
    def download_shopping_list(self, request):
        """Загрузка списка покупок."""

        # ingredients = Favourites.objects.filter(
        #     user=request.user, recipes=recipe
        # ).values(
        #     'ingredient__name',
        #     'ingredient__measurement_unit'
        # ).annotate(sum=Sum('amount'))

        ingredients = IngredientRecipe.objects.filter(
            recipe__author=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(sum=Sum('amount'))
        result = ''
        for ingredient in ingredients:
            result += (
                f"{ingredient['ingredient__name']}  - "
                f"{ingredient['sum']}"
                f"({ingredient['ingredient__measurement_unit']})\n"
            )
        return HttpResponse(result, content_type='text/plain')

    @action(methods=('POST', 'DELETE'),
            detail=True,
            permission_classes=(IsAuthenticated,),
            url_path='favorite',
            url_name='favorite')
    def favorite(self, request, pk=None):
        """Добавление рецепта в избранное."""
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if Favourites.objects.filter(user=request.user,
                                         recipe=recipe).exists():
                raise serializers.ValidationError(
                    'Невозможно повторно добавить рецепт в избранное!'
                )
            favorites = Favourites.objects.create(user=request.user,
                                                  recipe=recipe)
            serializer = FavoritesSerializer(favorites)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            delete_recipe, _ = Favourites.objects.filter(
                user=request.user, recipe=recipe
            ).delete()
            if not delete_recipe:
                raise serializers.ValidationError(
                    'Невозможно удалить рецепт из избранного, которого нет!'
                )
            return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeFavoritesViewSet(viewsets.ModelViewSet):
    """ViewSet для управления избранными рецептами."""

    serializer_class = FavoritesSerializer
    queryset = Favourites.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Favourites.objects.filter(user=self.request.user)

    @action(methods=('POST',), detail=False)
    def add_favorite(self, request, pk=None):
        """Добавление рецепта в избранное."""
        recipe = get_object_or_404(Recipe, id=pk)
        favorites = Favourites.objects.create(user=request.user,
                                              recipes=recipe)
        serializer = FavoritesSerializer(favorites)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=('DELETE',), detail=False)
    def remove_favorite(self, request, pk=None):
        """Удаление рецепта из избранного."""
        recipe = get_object_or_404(Recipe, id=pk)
        delete_recipe, _ = Favourites.objects.filter(
            user=request.user, recipes=recipe
        ).delete()
        if not delete_recipe:
            raise serializers.ValidationError(
                'Невозможно удалить рецепт из избранного, которого нет!'
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=('GET',))
    def favorite_recipes(self, request):
        """Получение списка избранных рецептов."""
        user = self.request.user
        queryset = Favourites.objects.filter(
            user=user
        ).select_related('recipes')
        serializer = FavoritesSerializer(queryset, many=True)
        return Response(serializer.data)
