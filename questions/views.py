from typing import Any
from django.views.generic.base import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django import http
from django.shortcuts import render
from django.urls import reverse, reverse_lazy

from questions import forms
from questions.models import Question, QuestionLike, Answer, AnswerLike
from questions import pagination

from core.mixins import CommonViewContextMixin


class NewQuestionsView(CommonViewContextMixin, TemplateView):
    template_name: str = "questions/index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context |= self.get_common_context(self.request)

        page_number = pagination.get_page_number_from(self.request)
        
        new_questions = Question.objects.get_new_questions(self.request.user if context["logined"] else None)
        
        page = pagination.get_page_of(new_questions, page_number)

        context["questions"] = page.object_list
        context["page"] = page

        return context
    

class HotQuestionsView(CommonViewContextMixin, TemplateView):
    template_name: str = "questions/hot.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context |= self.get_common_context(self.request)

        page_number: int = pagination.get_page_number_from(self.request)

        hot_questions = Question.objects.get_hot_questions(self.request.user if context["logined"] else None)

        page = pagination.get_page_of(hot_questions, page_number)

        context["questions"] = page.object_list
        context["page"] = page

        return context
    
    
class AnswerAddView(LoginRequiredMixin, CommonViewContextMixin, View):
    login_url = reverse_lazy("core:login")

    template_name: str = "questions/answers.html"
    http_method_names = ["post"]

    def post(self, request: http.HttpRequest, question_id: int):
        context = self.get_common_context(request)
        form = forms.AddAnswerForm(request, question_id, request.POST)
        context["form"] = form

        if form.is_valid():
            form.save()
            return http.HttpResponseRedirect(reverse("questions:question", kwargs={"question_id": question_id}))

        return render(request, self.template_name, context=context)
    

class QuestionLikeAddView(CommonViewContextMixin, View):
    http_method_names = ["post"]

    def post(self, request: http.HttpRequest, question_id: int):
        user_logined = self.is_user_logined(request)
        if not user_logined:
            return http.JsonResponse({}, status=401)

        like_type = request.GET.get("type")
        if like_type is None or not QuestionLike.is_valid_type(like_type):
            return http.JsonResponse({}, status=400)
        
        question = Question.objects.filter(id=question_id).first()
        like = QuestionLike.objects.add_to(question, like_type, request.user)
        if like is None:
            return http.JsonResponse({}, status=403)
        
        return http.JsonResponse({"question_like_id": f"{like.pk}"}, status=200)
    

class AnswerLikeAddView(CommonViewContextMixin, View):
    http_method_names = ["post"]

    def post(self, request: http.HttpRequest, answer_id: int):
        user_logined = self.is_user_logined(request)
        if not user_logined:
            return http.JsonResponse({}, status=401)

        like_type = request.GET.get("type")
        if like_type is None or not AnswerLike.is_valid_type(like_type):
            return http.JsonResponse({}, status=400)

        answer = Answer.objects.filter(id=answer_id).first()
        like = AnswerLike.objects.add_to(answer, like_type, request.user)
        if like is None:
            return http.JsonResponse({}, status=403)

        return http.JsonResponse({"answer_like_id":f"{like.pk}"}, status=200)


class QuestionView(CommonViewContextMixin, TemplateView):
    template_name: str = "questions/answers.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = self.get_common_context(self.request)
        question_id = kwargs["question_id"]

        question = Question.objects.get_question_by_id(question_id, self.request.user if context["logined"] else None)
    
        page_number = pagination.get_page_number_from(self.request)

        answers = Question.objects.get_answers(question_id, self.request.user if context["logined"] else None)

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
        context |= self.get_common_context(self.request)
        tag_name: str = kwargs["tag_name"]

        page_number = pagination.get_page_number_from(self.request)

        questions_with_tag = Question.objects.get_questions_with_tag(tag_name, self.request.user if context["logined"] else None)

        page = pagination.get_page_of(questions_with_tag, page_number)

        context["questions"] = page.object_list
        context["page"] = page
        context["tag"] = tag_name

        return context
    

class AskView(LoginRequiredMixin, CommonViewContextMixin, View):
    login_url = reverse_lazy("core:login")

    template_name: str = "questions/ask.html"
    http_method_names = ["post", "get"]

    def get(self, request: http.HttpRequest):
        context = self.get_common_context(request)
        context["form"] = forms.AskForm(request)

        return render(request, self.template_name, context=context)
    
    def post(self, request: http.HttpRequest):
        context = self.get_common_context(request)
        form = forms.AskForm(request, request.POST)
        context["form"] = form

        if form.is_valid():
            question = form.save()
            return http.HttpResponseRedirect(reverse("questions:question", args=[question.pk]))
        
        return render(request, self.template_name, context=context)
