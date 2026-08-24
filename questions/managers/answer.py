from django.db import models

class AnswerManager(models.Manager):
    def set_correct(self, answer_id: int):
        self.filter(id=answer_id).update(is_correct=True)