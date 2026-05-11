from django.contrib.auth.models import User
from django.db.models import Count
from application import config
from dataclasses import dataclass


LINK_TYPES = [
    "link-primary",
    "link-danger",
    "link-warning",
    "link-secondary",
    "link-success"
]


@dataclass(frozen=True)
class BestMemberDisplay:
    username: str
    link_type: str


def get_best_members():
    return [ BestMemberDisplay(u.username, LINK_TYPES[i % len(LINK_TYPES)]) \
        for i, u in enumerate(User.objects.annotate(
            questions_count=Count("questions", distinct=True),
            answers_count=Count("answers", distinct=True)
        ).order_by("-questions_count", "-answers_count")[:config.BEST_MEMBERS_COUNT])
    ]
