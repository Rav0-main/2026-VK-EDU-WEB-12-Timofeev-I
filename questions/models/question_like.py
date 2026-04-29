from django.db import models
from django.utils.translation import gettext as _

class QuestionLike(models.Model):
    question = models.ForeignKey(
        "Question", on_delete=models.CASCADE, verbose_name=_("Вопрос"), related_name="likes"
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
            "question", "author"
        ]

        verbose_name = _("Лайк вопроса")
        verbose_name_plural = _("Лайки вопросов")

    def __str__(self):
        return _(f"Лайк на вопрос: {self.question.title}, тип: \"{self.type}\", автор: {self.author}")
    