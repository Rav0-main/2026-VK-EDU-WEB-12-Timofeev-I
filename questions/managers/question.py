from django.db import models

class QuestionManager(models.Manager):
    def get_new_questions(self, limit: int, offset: int):
        return self.order_by("-published_datetime")[offset: offset+limit]
    
    def get_hot_questions(self, limit: int, offset: int):
        return self.annotate(likes_count=models.Count("likes")) \
            .order_by("-likes_count", "-published_datetime")[offset: offset + limit]