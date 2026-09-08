from django.db import models


class AnswerManager(models.Manager):
    def set_correct(self, answer_id: int):
        self.filter(id=answer_id).update(is_correct=True)

    def calc_vote_count_of(self, answer_id: int) -> int:
        answer = (
            self.filter(id=answer_id)
            .annotate(vote_count=models.Sum("likes__type"))
            .first()
        )

        return answer.vote_count if answer else 0
