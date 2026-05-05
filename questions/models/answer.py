from django.db import models
from django.utils.translation import gettext as _


class Answer(models.Model):
    question = models.ForeignKey(
        "Question", on_delete=models.CASCADE, verbose_name=_("Вопрос"),
        related_name="answers"
    )
    author = models.ForeignKey("auth.User", on_delete=models.CASCADE, verbose_name=_("Автор"))

    content = models.TextField(max_length=4000, verbose_name=_("Текст"))
    is_correct = models.BooleanField(verbose_name=_("Это правильный ответ?"), default=False)
    published_datetime = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Дата публикации")
    )

    class Meta:
        unique_together = [
            "question", "author", "content"
        ]

        verbose_name = _("Ответ")
        verbose_name_plural = _("Ответы")

    def __str__(self) -> str:
        return _(f"Ответ на: {self.question.title}, правильность: {self.is_correct}, автор: {self.author}")
    