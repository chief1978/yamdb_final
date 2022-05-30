from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель кастомизированного пользователя.
    Необязательное поле password, необходимое только для суперюзера.
    """
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    USER_ROLE = (
        (ADMIN, 'admin'),
        (MODERATOR, 'moderator'),
        (USER, 'user'),
    )
    password = models.CharField(
        'Пароль',
        max_length=128,
        blank=True,
        null=True,
    )
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(
        'Роль',
        max_length=20,
        choices=USER_ROLE,
        default=USER
    )

    class Meta:
        ordering = ('-date_joined',)

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    def save(self, *args, **kwargs):
        if self.role == self.ADMIN:
            self.is_staff = True
        super().save(*args, **kwargs)
