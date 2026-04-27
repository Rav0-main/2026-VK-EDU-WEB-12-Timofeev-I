from django.db import models
from django.utils.translation import gettext as _
from questions import managers
from application import questions

class Tag(models.Model):
    objects: managers.TagManager = managers.TagManager()

    question = models.ForeignKey(
        "Question", on_delete=models.CASCADE, verbose_name=_("Вопрос"),
        related_name="tags"
    )

    name = models.CharField(max_length=127, verbose_name=_("Название"))

    class Meta:
        unique_together = [
            "name", "question"
        ]

        verbose_name = _("Тег")
        verbose_name_plural = _("Теги")

    def __str__(self) -> str:
        return _(f"Тег: {self.name}")
    
    @staticmethod
    def get_tops_str(count: int):
        return questions.form_popular_tags(
            list(Tag.objects.get_tops(count).values_list("name", flat=True)),
        )[:count]