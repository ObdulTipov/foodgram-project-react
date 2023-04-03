from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    REQUIRED_FIELDS = ('first_name', 'last_name', 'username',)
    USERNAME_FIELD = 'email'
    USER = 'user'
    ADMIN = 'admin'
    ROLES = [
        (USER, USER),
        (ADMIN, ADMIN),
    ]

    email = models.EmailField(
        max_length=254, unique=True, blank=False,
        verbose_name='Электронная почта',
    )
    role = models.CharField(
        max_length=20, choices=ROLES,
        default=USER, verbose_name='Право достапа',
    )
    bio = models.TextField(
        blank=True, verbose_name='Биография',
    )
    confirmation_code = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name='Код подтверждения',
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username
