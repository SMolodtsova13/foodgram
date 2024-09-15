from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint

from api_foodgram.constans import NAME_MAX_LENGTH, EMAIL_MAX_LENGTH


class UserRoles(models.TextChoices):

    USER = 'user', 'Пользователь'
    ADMINISTRATOR = 'admin', 'Администратор'


max_length = max(len(role) for role in UserRoles.choices)


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
    role = models.CharField('Роль пользователя',
                            choices=UserRoles.choices,
                            max_length=NAME_MAX_LENGTH,
                            default=UserRoles.USER)
    password = models.CharField(blank=False,
                                max_length=EMAIL_MAX_LENGTH)

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = (UniqueConstraint(
            fields=('username', 'email'),
            name='unique_user',
        ),)

    def __str__(self):
        return self.username[:50]

    @property
    def is_admin(self):
        return (self.is_superuser
                or self.is_staff
                or self.role == UserRoles.ADMINISTRATOR.value)

    @property
    def is_user(self):
        return self.role == UserRoles.USER.value


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
        constraints = (UniqueConstraint(
            fields=('user', 'author'),
            name='unique_follow',
        ),)

    def __str__(self):
        return f'{self.user.username} подписался на {self.author.username}'
