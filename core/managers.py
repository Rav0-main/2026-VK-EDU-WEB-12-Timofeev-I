from django.contrib.auth.models import User
from django.db.models import Count
from application import config

def get_best_members():
    return User.objects.annotate(
        questions_count=Count("questions", distinct=True),
        answers_count=Count("answers", distinct=True)
    ).order_by("-questions_count", "-answers_count")[:config.BEST_MEMBERS_COUNT]