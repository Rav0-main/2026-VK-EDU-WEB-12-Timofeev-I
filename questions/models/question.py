from django.db import models
from django.utils.translation import gettext as _
from questions import managers

class Question(models.Model):
    objects: managers.QuestionManager = managers.QuestionManager()
    author = models.ForeignKey("auth.User", on_delete=models.CASCADE, verbose_name=_("Автор"),
                               related_name="questions")
    
    title = models.CharField(max_length=255, verbose_name=_("Заголовок"))
    content = models.TextField(max_length=4095, verbose_name=_("Текст"))

    published_datetime = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Дата публикации")
    )

    class Meta:
        unique_together = [
            "title", "content"
        ]

        verbose_name = _("Вопрос")
        verbose_name_plural = _("Вопросы")

    def __str__(self) -> str:
        return _(f"\"{self.title}\": @{self.author}")