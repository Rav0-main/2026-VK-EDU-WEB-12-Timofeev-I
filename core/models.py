from django.db import models
from django.utils.translation import gettext as _


class UserProfile(models.Model):
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE, verbose_name=_("Пользователь"))

    avatar = models.ImageField(upload_to="avatars/", verbose_name=_("Аватарка"), null=True, blank=True)

    class Meta:
        verbose_name = _("Профиль пользователя")
        verbose_name_plural = _("Профили пользователей")

    def __str__(self) -> str:
        return _(f"Профиль пользователя: {self.user.username}.")
