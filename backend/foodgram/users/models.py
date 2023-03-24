from django.contrib.auth.models import AbstractUser
from django.db import models
# from reviews.validators import validate_username


class User(AbstractUser):
    ADMIN = 'admin'
    USER = 'user'
    USER_ROLES = (
        (ADMIN, 'Admin role'),
        (USER, 'User role'),
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        # validators=(validate_username,),
        null=False
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        null=False)
    role = models.CharField(
        max_length=10,
        choices=USER_ROLES,
        default='user',
    )
    bio = models.TextField(
        'Биография',
        blank=True,
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    def __str__(self):
        return self.username
