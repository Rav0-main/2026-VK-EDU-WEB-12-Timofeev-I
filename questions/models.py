from django.db import models
from django.utils.translation import gettext as _


class Question(models.Model):
    author = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    
    title = models.CharField(max_length=255, verbose_name=_("Заголовок"))
    content = models.TextField(max_length=4000, verbose_name=_("Текст"))

    class Meta:
        unique_together = [
            "title", "content"
        ]

        verbose_name = _("Вопрос")
        verbose_name_plural = _("Вопросы")


class QuestionLike(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    author = models.ForeignKey("auth.User", on_delete=models.CASCADE)

    class Types:
        positive = "+"
        positive_verbose = _("Положительный")

        negative = "-"
        negative_verbose = _("Отрицательный")

        types = [
            (positive, positive_verbose),
            (negative, negative_verbose)
        ]

    type = models.CharField(max_length=32, choices=Types.types)

    class Meta:
        unique_together = [
            "question", "author"
        ]

        verbose_name = _("Лайк вопроса")
        verbose_name_plural = _("Лайки вопросов")


class Tag(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name=_("Заголовок"))

    class Meta:
        verbose_name = _("Тег")
        verbose_name_plural = _("Теги")


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    author = models.ForeignKey("auth.User", on_delete=models.CASCADE)

    content = models.TextField(max_length=4000, verbose_name=_("Текст"))
    is_correct = models.BooleanField(verbose_name=_("Это правильный ответ?"))

    class Meta:
        unique_together = [
            "author", "content"
        ]

        verbose_name = _("Ответ")
        verbose_name_plural = _("Ответы")


class AnswerLike(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    author = models.ForeignKey("auth.User", on_delete=models.CASCADE)

    class Types:
        positive = "+"
        positive_verbose = _("Положительный")

        negative = "-"
        negative_verbose = _("Отрицательный")

        types = [
            (positive, positive_verbose),
            (negative, negative_verbose)
        ]

    type = models.CharField(max_length=32, choices=Types.types)

    class Meta:
        unique_together = [
            "answer", "author"
        ]

        verbose_name = _("Лайк ответа")
        verbose_name_plural = _("Лайки ответов")
