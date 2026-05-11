from django.db import models
from django.utils.translation import gettext as _


class UserProfile(models.Model):
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE, verbose_name=_("Пользователь"))

    avatar_path = models.CharField(max_length=255, verbose_name=_("Путь к аватару"), null=True)

    class Meta:
        verbose_name = _("Профиль пользователя")
        verbose_name_plural = _("Профили пользователей")
