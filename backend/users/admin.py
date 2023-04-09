from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import User


class UserAdmin(admin.ModelAdmin):
    list_filter = ('username', 'email',)
    search_fields = ('username', 'email',)
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
