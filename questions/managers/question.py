from django.db import models
from django.core import exceptions
from django.db.models.query import QuerySet


class QuestionManager(models.Manager):
    def get_questions_with_tag(self, tag_name: str) -> QuerySet:
        return self.__form_question_query_set(self.filter(tags__content__name=tag_name))

    def get_new_questions(self) -> QuerySet:
        return self.__form_question_query_set(self.order_by("-published_datetime"))
    
    def get_question_by_id(self, question_id: int) -> QuerySet | None:
        try:
            return self.__form_question_query_set(self.all()).get(id=question_id)
        
        except exceptions.ObjectDoesNotExist:
            return None
        
    def get_answers(self, question_id: int) -> QuerySet | None:
        try:
            return self.get(id=question_id).answers \
                        .all().annotate(vote_count=models.Sum("likes__type")) \
                        .order_by("-is_correct", "-vote_count", "-published_datetime")

        except exceptions.ObjectDoesNotExist:
            return None
        
    def get_hot_questions(self) -> QuerySet:
        return self.__form_question_query_set(self.all()).order_by("-vote_count")
    
    def __form_question_query_set(self, query_set: QuerySet) -> QuerySet:
        return query_set.prefetch_related("answers", "likes", "tags", "tags__content") \
                        .annotate(vote_count=models.Sum("likes__type"),
                                  answers_count=models.Count("answers", distinct=True)
                                )
