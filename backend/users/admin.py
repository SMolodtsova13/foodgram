from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from users.models import Follow, FoodgramUser

User = get_user_model()


admin.site.unregister(Group)


@admin.register(FoodgramUser)
class FoodgramUserAdmin(admin.ModelAdmin):
    """Создание объекта пользователя в админ панели."""
    list_display = (
        'username', 'email', 'first_name', 'last_name'
    )
    list_filter = ('email', 'username')
    search_fields = ('email', 'username')
    empty_value_display = 'Поле не заполнено'


@admin.register(Follow)
class SubscriptionAdmin(admin.ModelAdmin):
    """Создание объекта подписки в админ панели."""

    list_display = ('id', 'user', 'author')
    search_fields = ('user', 'author')
    empty_value_display = 'Поле не заполнено'
