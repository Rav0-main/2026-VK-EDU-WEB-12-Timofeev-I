from django import http
from questions.models.tag import Tag
from core.models import UserProfile
from core.managers import get_best_members

class CommonViewContextMixin:
    def get_common_context_data(self, request: http.HttpRequest):
        context = {}

        context["logined"] = request.user.is_authenticated and request.user.is_active
        context["popular_tags"] = Tag.objects.get_popular_tags()
        context["best_members"] = get_best_members()
        context["current_url"] = request.path
        
        if context["logined"]:
            try:
                context["user_nickname"] = request.user.profile.nickname
            except UserProfile.DoesNotExist:
                context["user_nickname"] = request.user.username

        return context