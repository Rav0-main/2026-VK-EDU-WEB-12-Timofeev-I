from django.db import models
from django.utils.translation import gettext as _
from questions.models._like_type import LikeType
from questions.managers.question_like import QuestionLikeManager

class QuestionLike(models.Model):
    objects: QuestionLikeManager = QuestionLikeManager()
    
    question = models.ForeignKey(
        "Question", on_delete=models.CASCADE, verbose_name=_("Вопрос"), related_name="likes"
    )
    author = models.ForeignKey("auth.User", on_delete=models.CASCADE, verbose_name=_("Автор"))

    class Types:
        positive: LikeType = 1
        positive_verbose = _("Положительный")

        negative: LikeType = -1
        negative_verbose = _("Отрицательный")

        types = [
            (positive, positive_verbose),
            (negative, negative_verbose)
        ]

    type = models.SmallIntegerField(choices=Types.types, verbose_name="Тип лайка")

    class Meta:
        unique_together = [
            "question", "author"
        ]

        verbose_name = _("Лайк вопроса")
        verbose_name_plural = _("Лайки вопросов")

    def __str__(self):
        return _(f"Лайк на вопрос: {self.question.title}, тип: \"{self.type}\", автор: {self.author}")
    