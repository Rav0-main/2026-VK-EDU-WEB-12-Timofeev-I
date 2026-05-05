from django.db import models
from django.core import exceptions
from dataclasses import dataclass
from datetime import datetime

from questions.models.question_like import QuestionLike
from questions.models.answer_like import AnswerLike

class QuestionManager(models.Manager):
    def get_questions_with_tag(
            self, tag_name: str, page_number: int, questions_per_page: int
        ) -> 'list[QuestionDisplay]':
        return [
            self.__form_question(q) \
            for q in self.filter(tags__content__name=tag_name)
        ]#[(page_number-1) * questions_per_page: page_number * questions_per_page]

    def get_new_questions(
            self, page_number: int, questions_per_page: int
        ) -> 'list[QuestionDisplay]':
        return [
            self.__form_question(q) \
            for q in self.all().order_by("-published_datetime").prefetch_related("tags")
        ]#[(page_number-1) * questions_per_page: page_number * questions_per_page]
    
    def get_question_by_id(self, question_id: int) -> 'QuestionDisplay | None':
        try:
            q = self.get(id=question_id)
            return self.__form_question(q)
        
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
                    vote_count=answer.likes.filter(type=AnswerLike.Types.positive).count() - \
                        answer.likes.filter(type=AnswerLike.Types.negative).count(),
                    published_datetime=answer.published_datetime,
                    is_correct=answer.is_correct
                )
                for answer in self.get(id=question_id).answers.prefetch_related("likes")
            ]

        except exceptions.ObjectDoesNotExist:
            return []

        answers_list.sort(key=lambda answer: (
            answer.is_correct, answer.vote_count, answer.published_datetime
        ), reverse=True)

        return answers_list#[(page_number-1) * answers_per_page: page_number * answers_per_page]
        
    def get_hot_questions(
            self, page_number: int, questions_per_page: int
        ) -> 'list[QuestionDisplay]':
        #вкусняшка
        questions_list = [
            self.__form_question(q) \
            for q in self.all().prefetch_related("likes", "answers", "tags")
        ]

        questions_list.sort(key=lambda q: q.vote_count, reverse=True)

        return questions_list#[
            #(page_number - 1) * questions_per_page:
            #page_number * questions_per_page
        #]
    
    def __form_question(self, question) -> 'QuestionDisplay':
        return QuestionDisplay(
            id=question.id,
            title=question.title,
            content=question.content,
            tags=[
                tag.content.name for tag in question.tags.all()
            ],
            published_datetime=question.published_datetime,
            answer_count=question.answers.count(),
            vote_count=question.likes.filter(type=QuestionLike.Types.positive).count() - \
                question.likes.filter(type=QuestionLike.Types.negative).count()
        )


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