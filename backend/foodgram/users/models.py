from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    REQUIRED_FIELDS = ('first_name', 'last_name', 'username',)
    USERNAME_FIELD = 'email'
    ADMIN = 'admin'
    USER = 'user'
    USER_ROLES = (
        (USER, USER),
        (ADMIN, ADMIN),
    )

    email = models.EmailField(max_length=254, unique=True, blank=False)
    role = models.CharField(max_length=10, choices=USER_ROLES, default=USER)
    bio = models.TextField(blank=True)
    confirmation_code = models.CharField(
        max_length=255, blank=True, null=True
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
