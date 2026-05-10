from django.db import models
from django.core import exceptions
from dataclasses import dataclass
from datetime import datetime

"""
ИЗ-ЗА СОЗДАНИЯ МАССИВА ПИТОН ЖРЁТ ВРЕМЯ КАК СОБАКА.
ПОПРОБОВАТЬ ПЕРЕКИНУТЬ НЕ МАССИВ, А КВЕРИ-СЕТ В ШАБЛОН.
"""

class QuestionManager(models.Manager):
    def get_questions_with_tag(
            self, tag_name: str, page_number: int, questions_per_page: int
        ) -> 'list[QuestionDisplay]':
        return [
            self.__form_question_view(q) \
            for q in self.__form_question_query_set(self.filter(tags__content__name=tag_name))
        ]#[(page_number-1) * questions_per_page: page_number * questions_per_page]

    def get_new_questions(
            self, page_number: int, questions_per_page: int
        ) -> 'list[QuestionDisplay]':
        return [
            self.__form_question_view(q) \
            for q in self.__form_question_query_set(self.order_by("-published_datetime"))
        ]#[(page_number-1) * questions_per_page: page_number * questions_per_page]
    
    def get_question_by_id(self, question_id: int) -> 'QuestionDisplay | None':
        try:
            q = self.__form_question_query_set(self.all()).get(id=question_id)
            return self.__form_question_view(q)
        
        except exceptions.ObjectDoesNotExist:
            return None
        
    def get_answers(
            self, question_id: int, page_number: int, answers_per_page: int
        ) -> 'list[AnswerDisplay]':
        try:
            answers_list = [
                AnswerDisplay(
                    id=answer.id,
                    content=answer.content,
                    vote_count=answer.vote_count,
                    published_datetime=answer.published_datetime,
                    is_correct=answer.is_correct
                )
                for answer in self.get(id=question_id).answers \
                              .all().annotate(vote_count=models.Sum("likes__type")) \
                              .order_by("-is_correct", "-vote_count", "-published_datetime")
            ]

        except exceptions.ObjectDoesNotExist:
            return []

        return answers_list#[(page_number-1) * answers_per_page: page_number * answers_per_page]
        
    def get_hot_questions(
            self, page_number: int, questions_per_page: int
        ) -> 'list[QuestionDisplay]':
        return [
            self.__form_question_view(q) \
            for q in self.__form_question_query_set(self.all()).order_by("-vote_count")
        ]
    
    def __form_question_view(self, question) -> 'QuestionDisplay':
        return QuestionDisplay(
            id=question.id,
            title=question.title,
            content=question.content,
            tags=[
                tag.content.name for tag in question.tags.all()
            ],
            published_datetime=question.published_datetime,
            answer_count=question.answers.count(),
            vote_count=question.vote_count,
        )
    
    def __form_question_query_set(self, query_set):
        return query_set.prefetch_related("answers", "likes", "tags", "tags__content") \
                        .annotate(vote_count=models.Sum("likes__type"))


@dataclass(frozen=True)
class QuestionDisplay:
    id: int
    title: str
    content: str
    tags: list[str]
    published_datetime: datetime
    answer_count: int
    vote_count: int


@dataclass(frozen=True)
class AnswerDisplay:
    id: int
    content: str
    vote_count: int
    published_datetime: datetime
    is_correct: bool