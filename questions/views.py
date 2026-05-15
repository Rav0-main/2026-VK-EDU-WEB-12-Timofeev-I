from typing import Any
from django.views.generic.base import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django import http
from django.shortcuts import render
from django.urls import reverse, reverse_lazy

from questions import forms
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
    
class AddAnswerView(LoginRequiredMixin, CommonViewContextMixin, View):
    login_url = reverse_lazy("core:login")

    template_name: str = "questions/answers.html"
    http_method_names = ["post"]

    def post(self, request: http.HttpRequest, question_id: int):
        context = self.get_common_context_data(request)
        form = forms.AddAnswerForm(request, question_id, request.POST)
        context["form"] = form

        if form.is_valid():
            form.save()
            return http.HttpResponseRedirect(reverse("questions:question", kwargs={"question_id": question_id}))

        return render(request, self.template_name, context=context)

class QuestionView(CommonViewContextMixin, TemplateView):
    template_name: str = "questions/answers.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = self.get_common_context_data(self.request)
        question_id = kwargs["question_id"]

        question = Question.objects.get_question_by_id(question_id)
    
        page_number = pagination.get_page_number_from(self.request)

        answers = Question.objects.get_answers(question_id)

        page = pagination.get_page_of(answers, page_number)

        context["question"] = question
        context["page"] = page
        context["answers"] = page.object_list
        context["form"] = forms.AddAnswerForm(self.request, question_id)

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
    

class AskView(LoginRequiredMixin, CommonViewContextMixin, View):
    login_url = reverse_lazy("core:login")

    template_name: str = "questions/ask.html"
    http_method_names = ["post", "get"]

    def get(self, request: http.HttpRequest):
        context = self.get_common_context_data(request)
        context["form"] = forms.AskForm(request)

        return render(request, self.template_name, context=context)
    
    def post(self, request: http.HttpRequest):
        context = self.get_common_context_data(request)
        form = forms.AskForm(request, request.POST)
        context["form"] = form

        if form.is_valid():
            question = form.save()
            return http.HttpResponseRedirect(reverse("questions:question", args=[question.pk]))
        
        return render(request, self.template_name, context=context)
