from typing import Any
from django import http
from questions.models.tag import Tag
from core.models import UserProfile
from core.managers import get_best_members
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings

class CommonViewContextMixin:
    def get_common_context(self, request: http.HttpRequest):
        context = {}

        context["logined"] = request.user.is_authenticated and request.user.is_active
        context["popular_tags"] = Tag.objects.get_popular_tags()
        context["best_members"] = get_best_members()
        context["current_url"] = request.path
        
        if context["logined"]:
            try:
                context["user_nickname"] = request.user.profile.nickname
                context["avatar_url"] = request.user.profile.avatar.url
                
            except UserProfile.DoesNotExist:
                context["user_nickname"] = request.user.username
                context["avatar_url"] = "#"

        return context


class UserFieldsPrepareMixin:
    def prepare_user_data(self, user_data: dict[str, Any]):
        user_data["username"] = self.get_username(user_data.get("username"))
        user_data["email"] = self.get_email(user_data.get("email"))
        user_data["nickname"] = self.get_nickname(user_data.get("nickname"))

    def get_username(self, username: str | None) -> str | None:
        return None if username is None else username.strip().lower()

    def get_email(self, email: str | None) -> str | None:
        return None if email is None else email.strip()
    
    def get_nickname(self, nickname: str | None) -> str | None:
        return None if nickname is None else nickname.strip()
    

class RedirectUrlValidatorMixin:
    def is_valide_redirect_url(self, request: http.HttpRequest, redirect_url: str) -> bool:
        return redirect_url is not None and redirect_url != "" and \
            url_has_allowed_host_and_scheme(
                url=redirect_url,
                allowed_hosts={request.get_host(), *settings.ALLOWED_HOSTS},
            )