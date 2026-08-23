from django.db import models
from django.db.utils import IntegrityError
from questions.models._like_type import is_valid_like_type

class QuestionLikeManager(models.Manager):
    def add_to(self, question, like_type: str, user):
        if question is None:
            return None   
        elif not is_valid_like_type(like_type):
            return None
        elif question.likes.filter(author=user).exists():
            return None
        
        try:
            return self.create(type=like_type, question=question, author=user)
        
        except IntegrityError:
            return self.filter(type=like_type, question=question, author=user).first()
