from typing import Any
from django.views.generic.base import TemplateView

from questions.models import Question
from questions import pagination

from core.mixins import CommonViewContextMixin


class NewQuestionsView(CommonViewContextMixin, TemplateView):
    template_name: str = "questions/index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        page_number = pagination.get_page_number_from(self.request)
        
        new_questions = Question.objects.get_new_questions()
        
        page = pagination.get_page_of(new_questions, page_number)
    
        context["questions"] = page.object_list
        context["page"] = page
        context |= self.get_common_context_data(self.request)

        return context
    

class HotQuestionsView(CommonViewContextMixin, TemplateView):
    template_name: str = "questions/hot.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        page_number: int = pagination.get_page_number_from(self.request)

        hot_questions = Question.objects.get_hot_questions()

        page = pagination.get_page_of(hot_questions, page_number)

        context["questions"] = page.object_list
        context["page"] = page
        context |= self.get_common_context_data(self.request)

        return context
    

class QuestionView(CommonViewContextMixin, TemplateView):
    template_name: str = "questions/answers.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        question_id = kwargs["question_id"]

        question = Question.objects.get_question_by_id(question_id)
    
        page_number = pagination.get_page_number_from(self.request)

        answers = Question.objects.get_answers(question_id)

        page = pagination.get_page_of(answers, page_number)

        context["question"] = question
        context["page"] = page
        context["answers"] = page.object_list
        context |= self.get_common_context_data(self.request)

        return context
    
    
class QuestionsByTagView(CommonViewContextMixin, TemplateView):
    template_name: str = "questions/tag.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        tag_name: str = kwargs["tag_name"]

        page_number = pagination.get_page_number_from(self.request)

        questions_with_tag = Question.objects.get_questions_with_tag(tag_name)

        page = pagination.get_page_of(questions_with_tag, page_number)

        context["questions"] = page.object_list
        context["page"] = page
        context["tag"] = tag_name
        context |= self.get_common_context_data(self.request)

        return context
    

class AskView(CommonViewContextMixin, TemplateView):
    template_name: str = "questions/ask.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context |= self.get_common_context_data(self.request)

        return context
