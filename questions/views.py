from typing import Any
from django.views.generic.base import TemplateView

from application import questions
from questions import pagination


class NewQuestionsView(TemplateView):
    template_name: str = "questions/index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        page_number: int = pagination.get_page_number_from(self.request)
        page = pagination.get_page_of(questions.QUESTIONS, page_number)

        context["questions"] = page.object_list
        context["page"] = page
        context["logined"] = False
        context["popular_tags"] = questions.get_popular_tags(questions.QUESTIONS)

        return context
    

class HotQuestionsView(TemplateView):
    template_name: str = "questions/hot.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        page_number: int = pagination.get_page_number_from(self.request)
        page = pagination.get_page_of(questions.QUESTIONS[::-1], page_number)

        context["questions"] = page.object_list
        context["page"] = page
        context["logined"] = False
        context["popular_tags"] = questions.get_popular_tags(questions.QUESTIONS)

        return context
    

class QuestionView(TemplateView):
    template_name: str = "questions/answers.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        number = kwargs["number"]

        question = questions.QUESTIONS[0]
        try:
            question = questions.QUESTIONS[number]
        except IndexError:
            pass
    
        page_number = pagination.get_page_number_from(self.request)

        page = pagination.get_page_of(questions.ANSWERS["correct"] + questions.ANSWERS["not_checked"], page_number)
        answers_page: dict[str, list[questions.Answer]] = {
            "correct": [obj for obj in page.object_list if obj.is_correct],
            "not_checked": [obj for obj in page.object_list if not obj.is_correct]
        }

        context["question"] = question
        context["answers"] = answers_page
        context["page"] = page
        context["logined"] = False
        context["popular_tags"] = questions.get_popular_tags(questions.QUESTIONS)

        return context
    
    
class QuestionsByTagView(TemplateView):
    template_name: str = "questions/tag.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        tag = kwargs["tag"]

        tag_lower = tag.lower()
        questions_with_tag: list[questions.Question] = [
            i for i in questions.QUESTIONS if tag_lower in map(lambda s: s.lower(), i.tags)
        ]

        page_number = pagination.get_page_number_from(self.request)

        page = pagination.get_page_of(questions_with_tag, page_number)

        context["questions"] = page.object_list
        context["page"] = page
        context["tag"] = tag
        context["logined"] = False
        context["popular_tags"] = questions.get_popular_tags(questions.QUESTIONS)

        return context
    

class AskView(TemplateView):
    template_name: str = "questions/ask.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["logined"] = True
        context["popular_tags"] = questions.get_popular_tags(questions.QUESTIONS)

        return context
