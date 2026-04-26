from django.contrib import admin
from core.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user", "nickname", "avatar_path"
    ]