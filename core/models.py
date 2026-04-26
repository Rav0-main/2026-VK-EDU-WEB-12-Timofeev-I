from django.db import models
from django.utils.translation import gettext as _


class UserProfile(models.Model):
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE)

    nickname = models.CharField(max_length=255, verbose_name=_("Псевдоним"))
    avatar_path = models.CharField(max_length=255, verbose_name=_("Путь к аватару"))

    class Meta:
        verbose_name = _("Профиль пользователя")
        verbose_name_plural = _("Профили пользователей")
