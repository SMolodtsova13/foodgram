import csv
from http.client import HTTPResponse
from io import StringIO

from django.contrib.auth import get_user_model
from django.http import Http404, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated, IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.serializers import (IngredientSerializer, FollowSerializer,
                             RecipeSerializer, CustomUserSerializer,
                             FavoritesSerializer, ShoppingListSerializer,
                             TagSerializer)
from api.filters import RecipeFilter
from api.permissions import IsAuthorOrReadOnlyPermission
from api.pagination import LimitPagination
from recipes.models import (IngredientRecipe, Tag, Ingredient, Favourites, Recipe, ShoppingList)
from users.models import Follow


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для управления пользователями."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.request.user

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=('GET',))
    def subscriptions(self, request):
        """Просмотр подписок пользователя."""
        user = self.request.user
        queryset = Follow.objects.filter(user=user).select_related('author')
        serializer = FollowSerializer(queryset,
                                      many=True,
                                      context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=('POST', 'DELETE',))
    def subscribe(self, request, id=None):
        """Подписка на автора."""
        user = self.request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            return Response({'errors': 'Нельзя подписаться/отписаться от себя!'},
                            status=status.HTTP_400_BAD_REQUEST)
        if Follow.objects.filter(user=user, author=author).exists():
            return Response({'errors': 'Подписка уже оформлена!'},
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            queryset = Follow.objects.create(author=author, user=user)
            serializer = FollowSerializer(queryset,
                                          context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
        queryset = Follow.objects.filter(user=user).values_list('author', flat=True)
        authors = User.objects.filter(id__in=queryset)
        serializer = CustomUserSerializer(authors, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=('GET',))
    def subscribed_by(self, request):
        """Список пользователей, подписанных на текущего автора."""
        author = self.request.user
        queryset = Follow.objects.filter(author=author).values_list('user', flat=True)
        users = User.objects.filter(id__in=queryset)
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение списка тегов, конкретного тега."""
    permission_classes = (IsAuthorOrReadOnlyPermission,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение списка ингредиентов, конкретного ингредиента."""
    permission_classes = (IsAuthorOrReadOnlyPermission,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для управления рецептами."""

    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnlyPermission,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['GET'], detail=False,
           permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Скачивание списка покупок"""
        shopping_result = {}
        ingredients = IngredientRecipe.objects.filter(
            recipes__shoppinglist__user=request.user
        ).values_list("ingredients__name",
                      "ingredients__measurement_unit",
                      "amount")
        for ingredient in ingredients:
            name = ingredient[0]
            if name not in shopping_result:
                shopping_result[name] = {
                    "measurement_unit": ingredient[1],
                    "amount": ingredient[2],
                }
            else:
                shopping_result[name]["amount"] += ingredient[2]
        shopping_itog = (
            f"{name} - {value['amount']} " f"{value['measurement_unit']}\n"
            for name, value in shopping_result.items()
        )
        response = HTTPResponse(shopping_itog, content_type="text/plain")
        response["Content-Disposition"] = \
            'attachment; filename="shoppinglist.txt"'
        return response


class ShoppingViewSet(viewsets.ModelViewSet):
    """ViewSet для управления списком покупок."""

    serializer_class = ShoppingListSerializer
    pagination_class = LimitPagination
    queryset = ShoppingList.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return ShoppingList.objects.filter(user=self.request.user)

    @action(methods=('POST',), detail=False)
    def add_shopping_item(self, request, pk=None):
        """Добавление рецепта в список покупок."""
        try:
            recipe = Recipe.objects.get(id=pk)
        except Recipe.DoesNotExist:
            raise Http404
        shopping_list = ShoppingList.objects.create(user=request.user,
                                                    recipes=recipe)
        serializer = ShoppingListSerializer(shopping_list)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=('DELETE',), detail=False)
    def remove_shopping_item(self, request, pk=None):
        """Удаление рецепта из списка покупок."""
        try:
            recipe = Recipe.objects.get(id=pk)
        except Recipe.DoesNotExist:
            raise Http404
        ShoppingList.objects.filter(user=request.user, recipes=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('GET',), detail=False)
    def download_shopping_list(self, request):
        """Загрузка списка покупок."""
        user = request.user
        queryset = ShoppingList.objects.filter(
            user=user
            ).select_related('recipes').order_by('created_at')
        serializer = ShoppingListSerializer(queryset, many=True)
        response = StreamingHttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="shopping_list_{user}.csv"'
        writer = csv.DictWriter(StringIO(), fieldnames=('recipe__title',
                                                        'recipe__description'))
        writer.writeheader()
        for item in serializer.data:
            writer.writerow({'recipe__title': item['recipe']['title'],
                             'recipe__description': item['recipe']['description']})
        response.write(writer.getvalue())
        return response


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
        Favourites.objects.filter(user=request.user, recipes=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=('GET',))
    def favorite_recipes(self, request):
        """Получение списка избранных рецептов."""
        user = self.request.user
        queryset = Favourites.objects.filter(user=user).select_related('recipes')
        serializer = FavoritesSerializer(queryset, many=True)
        return Response(serializer.data)
