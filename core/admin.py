from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from core.models import UserProfile


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    class UserProfileInline(admin.StackedInline):
        model = UserProfile
        can_delete = False

        verbose_name_plural = _("Профили пользователей")
        fields = [
            "nickname", "avatar_path"
        ]

    inlines = [UserProfileInline]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user", "nickname"
    ]
    
    search_fields = [
        "user__username", "nickname"
    ]
