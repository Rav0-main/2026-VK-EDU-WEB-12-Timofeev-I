from typing import Any
from django.views.generic.base import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django import http
from django.shortcuts import render
from django.urls import reverse, reverse_lazy

from application import config
from questions import forms
from questions.models import Question, QuestionLike, Answer, AnswerLike
from questions import pagination

from core.mixins import CommonViewContextMixin
from questions.tasks import (
    notificate_new_answer,
    publish_new_answer,
    publish_answer_correct,
    publish_answer_new_vote_count,
)


class NewQuestionsView(CommonViewContextMixin, TemplateView):
    template_name: str = "questions/index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context |= self.get_common_context(self.request)

        new_questions = Question.objects.get_new_questions(self.get_user())
        paginator = pagination.PaginationManager(
            self.request,
            new_questions,
            pagination.DEFAULT_PAGE_NUMBER,
            config.QUESTIONS_PER_PAGE,
        )

        context["pagination"] = paginator
        context["questions"] = paginator.page.object_list

        return context


class HotQuestionsView(CommonViewContextMixin, TemplateView):
    template_name: str = "questions/hot.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context |= self.get_common_context(self.request)

        hot_questions = Question.objects.get_hot_questions(self.get_user())
        paginator = pagination.PaginationManager(
            self.request,
            hot_questions,
            pagination.DEFAULT_PAGE_NUMBER,
            config.QUESTIONS_PER_PAGE,
        )

        context["questions"] = paginator.page.object_list
        context["pagination"] = paginator

        return context


class AnswerAddView(LoginRequiredMixin, CommonViewContextMixin, View):
    login_url = reverse_lazy("core:login")

    template_name: str = "questions/answers.html"
    http_method_names = ["post"]

    def post(self, request: http.HttpRequest, question_id: int):
        context = self.get_common_context(request)
        form = forms.AnswerAddForm(request, question_id, request.POST)

        if form.is_valid():
            answer = form.save()
            answers = Question.objects.get_answers(question_id, request.user)
            paginator = pagination.Paginator(answers, config.ANSWERS_PER_PAGE)
            answer_page = next(
                page_number
                for page_number in paginator.page_range
                if answer in paginator.page(page_number).object_list
            )
            answer_index = next(
                i
                for i, ans in enumerate(paginator.page(answer_page).object_list)
                if ans == answer
            )

            question_url = (
                reverse("questions:question", kwargs={"question_id": question_id})
                + f"?page={answer_page}"
            )

            answer_url = question_url + f"#answer-{answer.pk}"

            notificate_new_answer.delay(
                question_author_id=answer.question.author.id,
                answer_url=answer_url,
                author_nickname=answer.author.profile.nickname,
                message=answer.content,
            )

            publish_new_answer.delay(
                question_id=question_id,
                answer_id=answer.pk,
                question_url=question_url,
                answer_index=answer_index,
                author_nickname=answer.author.profile.nickname,
                author_avatar_url=answer.author.profile.avatar.url,
                answer_vote_count=0,
                content=answer.content,
            )

            return http.HttpResponseRedirect(answer_url)

        context["form"] = form
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

        answer: Answer | None = Answer.objects.filter(id=answer_id).first()
        like = AnswerLike.objects.add_to(answer, like_type, request.user)
        if answer is None or like is None:
            return http.JsonResponse({}, status=403)

        vote_count = Answer.objects.calc_vote_count_of(answer_id)
        publish_answer_new_vote_count.delay(
            answer_id=answer_id, new_vote_count=vote_count
        )

        return http.JsonResponse({"answer_like_id": f"{like.pk}"}, status=200)


class AnswerSetCorrectView(CommonViewContextMixin, View):
    http_method_names = ["post"]

    def post(self, request: http.HttpRequest, answer_id: int):
        user_logined = self.is_user_logined(request)
        if not user_logined:
            return http.JsonResponse({}, status=401)

        answer = Answer.objects.filter(id=answer_id).first()
        if answer is None:
            return http.JsonResponse({}, status=404)

        if answer.question.author != self.request.user:
            return http.JsonResponse({}, status=403)

        Answer.objects.set_correct(answer_id)
        publish_answer_correct.delay(answer_id=answer_id)

        return http.JsonResponse({"answer_id": answer_id}, status=200)


class QuestionView(CommonViewContextMixin, TemplateView):
    template_name: str = "questions/answers.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = self.get_common_context(self.request)
        question_id = kwargs["question_id"]

        question = Question.objects.get_question_by_id(question_id, self.get_user())
        user_is_question_author = Question.objects.is_question_author(
            self.get_user(), question
        )

        answers = Question.objects.get_answers(question_id, self.get_user())
        paginator = pagination.PaginationManager(
            self.request,
            answers,
            pagination.DEFAULT_PAGE_NUMBER,
            config.ANSWERS_PER_PAGE,
        )

        context["question"] = question
        context["pagination"] = paginator
        context["answers"] = paginator.page.object_list
        context["form"] = forms.AnswerAddForm(self.request, question_id)
        context["user_is_question_author"] = user_is_question_author

        return context


class QuestionsByTagView(CommonViewContextMixin, TemplateView):
    template_name: str = "questions/tag.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context |= self.get_common_context(self.request)
        tag_name: str = kwargs["tag_name"]

        questions_with_tag = Question.objects.get_questions_with_tag(
            tag_name, self.get_user()
        )
        paginator = pagination.PaginationManager(
            self.request,
            questions_with_tag,
            pagination.DEFAULT_PAGE_NUMBER,
            config.QUESTIONS_PER_PAGE,
        )

        context["questions"] = paginator.page.object_list
        context["pagination"] = paginator
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

        if form.is_valid():
            question = form.save()
            return http.HttpResponseRedirect(
                reverse("questions:question", args=[question.pk])
            )

        context["form"] = form
        return render(request, self.template_name, context=context)
