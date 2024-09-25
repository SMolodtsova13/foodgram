from django.contrib import admin
# from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from users.models import Follow, FoodgramUser

# User = get_user_model()

@admin.register(FoodgramUser)
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

# UserAdmin.fieldsets += (
#     ('Extra Fields', {'fields': ('avatar',
#                                  'role',
#                                  )}),
# )
# UserAdmin.list_display += (
#     'avatar',
#     'role',
# )
# UserAdmin.search_fields = ('email', 'username')
# UserAdmin.verbose_name = 'Пользователь'
# UserAdmin.actions += ('change_selected',
#                       'delete_selected')
# UserAdmin.empty_value_display = 'Поле не заполнено'
# admin.site.register(FoodgramUser, UserAdmin)


@admin.register(Follow)
class SubscriptionAdmin(admin.ModelAdmin):
    """Создание объекта подписки в админ панели."""

    list_display = ('id', 'user', 'author')
    search_fields = ('user', 'author')
    empty_value_display = 'Поле не заполнено'
