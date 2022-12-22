from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from core.models import User


@admin.register(User)
class CustomerAdmin(UserAdmin):
    """
    Добавление модели пользователя в django admin
    """
    list_display = ("username", "email", "first_name", "last_name")
    search_fields = ("username", "email", "first_name", "last_name")
    readonly_fields = ("last_login", "date_joined")
    fieldsets = (
        (None, {"fields": ("username", "first_name", "last_name", "email",
                           "is_active", "is_staff", "date_joined", "last_login")}),
    )


admin.site.unregister(Group)
