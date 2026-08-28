from django.contrib.auth.models import User
from django.db.models import Count, IntegerField, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce

from application import config
from dataclasses import dataclass
from questions.models.answer import Answer
from questions.models.question import Question


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


def get_best_members() -> list[BestMemberDisplay]:
    questions_count = Question.objects.filter(
        author=OuterRef("pk")
    ).values("author").annotate(count=Count("pk")).values("count")
    answers_count = Answer.objects.filter(
        author=OuterRef("pk")
    ).values("author").annotate(count=Count("pk")).values("count")

    usernames = User.objects.annotate(
        questions_count=Coalesce(
            Subquery(questions_count), Value(0), output_field=IntegerField()
        ),
        answers_count=Coalesce(
            Subquery(answers_count), Value(0), output_field=IntegerField()
        ),
    ).order_by("-questions_count", "-answers_count").values_list(
        "username", flat=True
    )[:config.BEST_MEMBERS_COUNT]

    return [
        BestMemberDisplay(username, LINK_TYPES[i % len(LINK_TYPES)])
        for i, username in enumerate(usernames)
    ]
