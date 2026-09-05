from typing import Any
from django import http
from questions.models.tag import Tag
from core.models import UserProfile
from core.managers import get_best_members
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
import jwt
from time import time

class CommonViewContextMixin:
    __slots__ = ["__user"]
    
    def get_common_context(self, request: http.HttpRequest):
        context = {}

        context["user_logined"] = self.is_user_logined(request)
        context["popular_tags"] = Tag.objects.get_popular_tags()
        context["best_members"] = get_best_members()
        context["current_url"] = request.path
        
        if context["user_logined"]:
            context["user_jwt_token"] = jwt.encode(
                {"sub": f"{request.user.pk}", "exp": int(time()) + 30 * 60},
                settings.CENTRIFUGE_HMAC_SECRET, algorithm="HS256"
            )
            context["user_id"] = request.user.pk

            try:
                context["user_nickname"] = request.user.profile.nickname
                self.__user = request.user
                if request.user.profile.avatar:
                    context["user_avatar_url"] = request.user.profile.avatar.url
                else:
                    context["user_avatar_url"] = "#"
                
            except UserProfile.DoesNotExist:
                context["user_nickname"] = request.user.username
                context["user_avatar_url"] = "#"
        else:
            self.__user = None

        return context

    def is_user_logined(self, request: http.HttpRequest):
        return request.user.is_authenticated and request.user.is_active

    def get_user(self):
        return self.__user


class UserFieldsPrepareMixin:
    def prepare_user_data(self, user_data: dict[str, Any]):
        user_data["username"] = self.prepare_username(user_data.get("username", ""))
        user_data["email"] = self.prepare_email(user_data.get("email", ""))
        user_data["nickname"] = self.prepare_nickname(user_data.get("nickname", ""))

    def prepare_username(self, username: str) -> str:
        return username.strip().lower()

    def prepare_email(self, email: str) -> str:
        return email.strip()
    
    def prepare_nickname(self, nickname: str) -> str:
        return nickname.strip()
    

class RedirectUrlValidatorMixin:
    def is_valid_redirect_url(self, request: http.HttpRequest, redirect_url: str) -> bool:
        return redirect_url is not None and redirect_url != "" and \
            url_has_allowed_host_and_scheme(
                url=redirect_url,
                allowed_hosts={request.get_host(), *settings.ALLOWED_HOSTS},
            )