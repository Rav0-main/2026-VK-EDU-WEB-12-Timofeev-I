from typing import Any
from django.views.generic.base import TemplateView

from application import config
from questions import models

class LoginView(TemplateView):
    template_name: str = "core/login.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["logined"] = False
        context["popular_tags"] = models.Tag.objects.get_popular_tags(
            config.POPULAR_TAGS_COUNT
        )

        return context


class RegisterView(TemplateView):
    template_name: str = "core/register.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["logined"] = False
        context["popular_tags"] = models.Tag.objects.get_popular_tags(
            config.POPULAR_TAGS_COUNT
        )

        return context


class ProfileView(TemplateView):
    template_name: str = "core/settings.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["logined"] = True
        context["popular_tags"] = models.Tag.objects.get_popular_tags(
            config.POPULAR_TAGS_COUNT
        )

        return context
