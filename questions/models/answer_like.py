from django.db import models
from django.utils.translation import gettext as _

class AnswerLike(models.Model):
    answer = models.ForeignKey(
        "Answer", on_delete=models.CASCADE, verbose_name=_("Ответ"), related_name="likes"
    )
    author = models.ForeignKey("auth.User", on_delete=models.CASCADE, verbose_name=_("Автор"))

    class Types:
        positive = "+"
        positive_verbose = _("Положительный")

        negative = "-"
        negative_verbose = _("Отрицательный")

        types = [
            (positive, positive_verbose),
            (negative, negative_verbose)
        ]

    type = models.CharField(max_length=32, choices=Types.types, verbose_name="Тип лайка")

    class Meta:
        unique_together = [
            "answer", "author"
        ]

        verbose_name = _("Лайк ответа")
        verbose_name_plural = _("Лайки ответов")

    def __str__(self):
        return _(f"Лайк на ответ: {self.answer.question.title}, тип: \"{self.type}\", автор лайка: {self.author}")