from django.db import models
from django.core import exceptions
from django.db.models.query import QuerySet
from django.db.models.functions import Coalesce
from questions.models.question_like import QuestionLike
from questions.models.answer import Answer

class QuestionManager(models.Manager):
    def get_questions_with_tag(self, tag_name: str, user=None) -> QuerySet:
        return self.__form_question_query_set(user) \
                .filter(tags__content__name=tag_name) \
                .order_by("-vote_count")

    def get_new_questions(self, user=None) -> QuerySet:
        return self.__form_question_query_set(user).order_by("-published_datetime")
    
    def get_question_by_id(self, question_id: int, user=None):
        try:
            return self.__form_question_query_set(user).get(id=question_id)
        
        except exceptions.ObjectDoesNotExist:
            return None
        
    def get_answers(self, question_id: int) -> QuerySet | list:
        try:
            return self.get(id=question_id).answers \
                        .all().annotate(vote_count=models.Sum("likes__type", default=0)) \
                        .order_by("-is_correct", "-vote_count", "-published_datetime")

        except exceptions.ObjectDoesNotExist:
            return []
        
    def get_hot_questions(self, user=None) -> QuerySet:
        return self.__form_question_query_set(user).order_by("-vote_count")
    
    def __form_question_query_set(self, user=None) -> QuerySet:
        vote_subquery = models.Subquery(
            QuestionLike.objects
            .filter(question=models.OuterRef('pk'))
            .values('question')
            .annotate(total=models.Sum('type'))
            .values('total')
        )

        answers_subquery = models.Subquery(
            Answer.objects
            .filter(question=models.OuterRef('pk'))
            .values('question')
            .annotate(count=models.Count('pk'))
            .values('count')
        )

        if user:
            user_liked_subquery = models.Subquery(
                QuestionLike.objects
                .filter(
                    question=models.OuterRef('pk'),
                    author=user
                )
                .values('type')[:1]
            )

            return self.annotate(
                vote_count=Coalesce(vote_subquery, 0),
                answers_count=Coalesce(answers_subquery, 0),
                user_liked=Coalesce(user_liked_subquery, 0)
            ).prefetch_related("tags__content", "author__profile")

        else:
            return self.annotate(
                vote_count=Coalesce(vote_subquery, 0),
                answers_count=Coalesce(answers_subquery, 0),
                user_liked=models.Value(0)
            ).prefetch_related("tags__content", "author__profile")
