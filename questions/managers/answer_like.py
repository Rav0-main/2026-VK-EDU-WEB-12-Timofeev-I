from django.db import models, IntegrityError
from questions.models._like_type import is_valid_like_type

class AnswerLikeManager(models.Manager):
    def add_to(self, answer, like_type: str, user):
        if answer is None:
            return None
        elif not is_valid_like_type(like_type):
            return None
        elif answer.likes.filter(author=user).exists():
            return None

        try:
            return self.create(type=like_type, answer=answer, author=user)

        except IntegrityError:
            return self.filter(type=like_type, answer=answer, author=user).first()
        