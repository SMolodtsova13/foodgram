from django.contrib import admin
from django.contrib.auth import get_user_model

from users.models import Follow

User = get_user_model()


@admin.register(User)
class FoodgramUserAdmin(admin.ModelAdmin):
    """Создание объекта пользователя в админ панели."""
    list_display = ('username',
                    'email',
                    'role',
                    'first_name',
                    'last_name',
                    'id')
    list_filter = ('email', 'username')
    search_fields = ('email', 'username')
    empty_value_display = 'Поле не заполнено'


@admin.register(Follow)
class SubscriptionAdmin(admin.ModelAdmin):
    """Создание объекта подписки в админ панели."""

    list_display = ('id', 'user', 'author')
    search_fields = ('user', 'author')
    empty_value_display = 'Поле не заполнено'
