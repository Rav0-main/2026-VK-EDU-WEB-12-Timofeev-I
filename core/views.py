from typing import Any
from django.views.generic.base import TemplateView

from application import questions

class LoginView(TemplateView):
    template_name: str = "core/login.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["logined"] = False
        context["popular_tags"] = questions.get_popular_tags(questions.QUESTIONS)

        return context


class RegisterView(TemplateView):
    template_name: str = "core/register.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["logined"] = False
        context["popular_tags"] = questions.get_popular_tags(questions.QUESTIONS)

        return context


class ProfileView(TemplateView):
    template_name: str = "core/settings.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["logined"] = True
        context["popular_tags"] = questions.get_popular_tags(questions.QUESTIONS)

        return context
