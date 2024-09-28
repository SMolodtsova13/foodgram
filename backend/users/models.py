from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
  

from recipes.constants import NAME_MAX_LENGTH, EMAIL_MAX_LENGTH


DEFAULT_AVATAR = 'users/avatar_default.jpg'


class FoodgramUser(AbstractUser):
    """Кастомная модель пользователей."""

    username = models.CharField(
        'Никнейм пользователя',
        max_length=NAME_MAX_LENGTH,
        unique=True,
        validators=(UnicodeUsernameValidator(),)
    )
    first_name = models.CharField(
        'Имя пользователя', max_length=NAME_MAX_LENGTH,
    )
    last_name = models.CharField(
        'Фамилия', max_length=NAME_MAX_LENGTH
    )
    email = models.EmailField(
        'Электронная почта',
        unique=True,
        max_length=EMAIL_MAX_LENGTH
        primary_key=True,
        db_index=True
    )
    avatar = models.ImageField(
        'Аватар профиля',
        upload_to='users',
        blank=True,
        null=True,
        default=DEFAULT_AVATAR
    )

    # objects = UserManager()

    class Meta:
        ordering = ('username', 'email',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username[:50]

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def get_short_name(self):
        return self.first_name

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']


class Follow(models.Model):
    """Модель подписчиков."""
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='publisher',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('user__username',)
        unique_together = ('user', 'author',)

    def __str__(self):
        return f'{self.user.username} подписался на {self.author.username}'

    def clean(self):
        if self.user == self.author:
            raise ValidationError({
                'user': 'Нельзя подписаться на самого себя!'
            })
        
        if Follow.objects.filter(user=self.user, author=self.author).exists():
            raise ValidationError({
                'user': 'Такая подписка уже существует!'
            })
