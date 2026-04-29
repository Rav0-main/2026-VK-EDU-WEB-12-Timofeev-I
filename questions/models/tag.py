from django.db import models
from django.utils.translation import gettext as _
from questions import managers

class Tag(models.Model):
    objects: managers.TagManager = managers.TagManager()

    question = models.ForeignKey(
        "Question", on_delete=models.CASCADE, verbose_name=_("Вопрос"),
        related_name="tags"
    )

    content = models.ForeignKey(
        "TagContent", on_delete=models.CASCADE, verbose_name=_("Содержимое тега"),
        related_name="tags"
    )

    class Meta:
        unique_together = [
            "question", "content"
        ]
        verbose_name = _("Тег")
        verbose_name_plural = _("Теги")

    def __str__(self) -> str:
        return _(f"На вопрос: {self.question}, {self.content}")
    

class TagContent(models.Model):
    name = models.CharField(max_length=127, verbose_name=_("Название"), unique=True)

    class Meta:
        verbose_name = "Содержимое тега"
        verbose_name_plural = "Содержимое тегов"

    def __str__(self):
        return _(f"Тег: {self.name}")
    