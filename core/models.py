from django.db import models
from django.utils.translation import gettext as _
from hashlib import sha256


def get_user_avatar_path(instance, filename: str) -> str:
    return f"avatars/{instance.user.date_joined.day:02d}/{instance.user.date_joined.month:02d}/" + \
           f"{instance.user.date_joined.year:02d}/{instance.user.pk}/{sha256(filename.encode()).hexdigest()}"


class UserProfile(models.Model):
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE, verbose_name=_("Пользователь"), related_name="profile")

    nickname = models.CharField(verbose_name=_("Отображаемое имя"), max_length=64)
    avatar = models.ImageField(upload_to=get_user_avatar_path, verbose_name=_("Аватарка"), null=True, blank=True)

    class Meta:
        verbose_name = _("Профиль пользователя")
        verbose_name_plural = _("Профили пользователей")

    def __str__(self) -> str:
        return _(f"Профиль пользователя: {self.user.username}.")
    