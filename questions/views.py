from typing import Any
from django.views.generic.base import TemplateView

from questions.models import Question, Tag
from application import config
from questions import pagination

"""
СДЕЛАТЬ НОРМ ГЕНЕРАЦИЮ ДАННЫХ ДЛЯ БД
СДЕЛАТЬ НОРМ ПАГИНАЦИЮ - ОПТИМИЗИРОВАТЬ: ВОЗВРАЩАТЬ ВСЮ БД В МАССИВЕ - СИЛЬНО
"""


class NewQuestionsView(TemplateView):
    template_name: str = "questions/index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        page_number = pagination.get_page_number_from(self.request)
        
        new_questions = Question.objects.get_new_questions(
            page_number, config.QUESTIONS_PER_PAGE
        )
        
        page = pagination.get_page_of(new_questions, page_number)
    
        context["questions"] = page.object_list
        context["page"] = page
        context["logined"] = False
        context["popular_tags"] = Tag.objects.get_popular_tags(config.POPULAR_TAGS_COUNT)

        return context
    

class HotQuestionsView(TemplateView):
    template_name: str = "questions/hot.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        page_number: int = pagination.get_page_number_from(self.request)

        hot_questions = Question.objects.get_hot_questions(
            page_number, config.QUESTIONS_PER_PAGE
        )

        page = pagination.get_page_of(
            hot_questions, page_number
        )

        context["questions"] = page.object_list
        context["page"] = page
        context["logined"] = False
        context["popular_tags"] = Tag.objects.get_popular_tags(config.POPULAR_TAGS_COUNT)

        return context
    

class QuestionView(TemplateView):
    template_name: str = "questions/answers.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        question_id = kwargs["question_id"]

        question = Question.objects.get_question_by_id(question_id)
    
        page_number = pagination.get_page_number_from(self.request)

        page = pagination.get_page_of(
            Question.objects.get_answers(
                question_id, page_number, config.ANSWERS_PER_PAGE
            ),
            page_number
        )

        context["question"] = question
        context["answers"] = page.object_list
        context["page"] = page
        context["logined"] = False
        context["popular_tags"] = Tag.objects.get_popular_tags(config.POPULAR_TAGS_COUNT)

        return context
    
    
class QuestionsByTagView(TemplateView):
    template_name: str = "questions/tag.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        tag_name: str = kwargs["tag_name"]

        page_number = pagination.get_page_number_from(self.request)

        questions_with_tag = Question.objects.get_questions_with_tag(
            tag_name, page_number, config.QUESTIONS_PER_PAGE
        )

        page = pagination.get_page_of(questions_with_tag, page_number)

        context["questions"] = page.object_list
        context["page"] = page
        context["tag"] = tag_name
        context["logined"] = False
        context["popular_tags"] = Tag.objects.get_popular_tags(config.POPULAR_TAGS_COUNT)

        return context
    

class AskView(TemplateView):
    template_name: str = "questions/ask.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["logined"] = True
        context["popular_tags"] = Tag.objects.get_popular_tags(config.POPULAR_TAGS_COUNT)

        return context
