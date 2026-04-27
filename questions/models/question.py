from django.db import models
from django.utils.translation import gettext as _
from questions import managers
from application import questions


class Question(models.Model):
    objects: managers.QuestionManager = managers.QuestionManager()
    author = models.ForeignKey("auth.User", on_delete=models.CASCADE, verbose_name=_("Автор"))
    
    title = models.CharField(max_length=255, verbose_name=_("Заголовок"))
    content = models.TextField(max_length=4095, verbose_name=_("Текст"))

    published_datetime = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата публикации"))

    class Meta:
        unique_together = [
            "title", "content"
        ]

        verbose_name = _("Вопрос")
        verbose_name_plural = _("Вопросы")

    def __str__(self) -> str:
        return _(f"\"{self.title}\": @{self.author}")
    
    @staticmethod
    def get_new_questions(page_number: int, questions_per_page: int):
        return Question.get_questions_list(
            Question.objects.get_new_questions(
                questions_per_page, (page_number - 1) * questions_per_page
            )
        )

    @staticmethod
    def get_questions_list(query: managers.QuestionManager):
        return [
            questions.Question(
                id=question.id,
                title=question.title,
                content=question.content,
                tags=[tag.name for tag in question.tags.all()],
                vote_count=question.likes.count(),
                answer_count=question.answers.count()
            )
            for question in query.prefetch_related("tags", "likes", "answers")
        ]
    

class QuestionLike(models.Model):
    question = models.ForeignKey("Question", on_delete=models.CASCADE, verbose_name=_("Вопрос"), related_name="likes")
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
    