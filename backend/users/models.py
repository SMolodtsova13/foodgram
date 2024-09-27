from django.contrib.auth.models import AbstractUser
from django.db import models

from recipes.constants import NAME_MAX_LENGTH, EMAIL_MAX_LENGTH


DEFAULT_AVATAR = 'users/avatar_default.jpg'


class FoodgramUser(AbstractUser):
    """Кастомная модель пользователей."""

    username = models.SlugField('Никнейм пользователя',
                                max_length=NAME_MAX_LENGTH,
                                blank=False,
                                unique=True)
    first_name = models.CharField('Имя пользователя',
                                  max_length=NAME_MAX_LENGTH,
                                  blank=False)
    last_name = models.CharField('Фамилия',
                                 blank=False,
                                 max_length=NAME_MAX_LENGTH)
    email = models.EmailField('Электронная почта',
                              unique=True,
                              blank=False,
                              max_length=EMAIL_MAX_LENGTH)
    avatar = models.ImageField('Аватар профиля',
                               upload_to='users',
                               blank=True,
                               null=True,
                               default=DEFAULT_AVATAR)

    # objects = UserManager()

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        # constraints = (UniqueConstraint(
        #     fields=('username', 'email'),
        #     name='unique_user',
        # ),)

    def __str__(self):
        return self.username[:50]


class Follow(models.Model):
    """Модель подписчиков."""
    user = models.ForeignKey(FoodgramUser,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Подписчик')
    author = models.ForeignKey(FoodgramUser,
                               on_delete=models.CASCADE,
                               related_name="publisher",
                               verbose_name="Автор")

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ('user__username',)

    def __str__(self):
        return f'{self.user.username} подписался на {self.author.username}'
