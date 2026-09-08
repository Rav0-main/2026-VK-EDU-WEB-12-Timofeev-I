from application.celery import app
from django.conf import settings
from questions.centrifuge import (
    NotificationCentrifugeManager,
    AnswerCentrifugeManager,
    AnswerLikeCentrifugeManager,
    AnswerCorrectCentrifugeManager,
)

notifications_manager = NotificationCentrifugeManager(
    settings.CENTRIFUGE_URL, settings.CENTRIFUGE_API_KEY
)
answers_manager = AnswerCentrifugeManager(
    settings.CENTRIFUGE_URL, settings.CENTRIFUGE_API_KEY
)
answer_like_manager = AnswerLikeCentrifugeManager(
    settings.CENTRIFUGE_URL, settings.CENTRIFUGE_API_KEY
)
answer_correct_manager = AnswerCorrectCentrifugeManager(
    settings.CENTRIFUGE_URL, settings.CENTRIFUGE_API_KEY
)


@app.task(ignore_result=True)
def notificate_new_answer(
    *, question_author_id: int, answer_url: str, author_nickname: str, message: str
):
    notifications_manager.notificate(
        question_author_id=question_author_id,
        answer_url=answer_url,
        author_nickname=author_nickname,
        message=message,
    )


@app.task(ignore_result=True)
def publish_new_answer(
    *,
    question_id: int,
    answer_id: int,
    question_url: str,
    answer_index: int,
    author_nickname: str,
    author_avatar_url: str,
    answer_vote_count: int,
    content: str,
):
    answers_manager.publish_answer(
        question_id=question_id,
        answer_id=answer_id,
        question_url=question_url,
        answer_index=answer_index,
        author_nickname=author_nickname,
        author_avatar_url=author_avatar_url,
        answer_vote_count=answer_vote_count,
        content=content,
    )


@app.task(ignore_result=True)
def publish_answer_new_vote_count(*, answer_id: int, new_vote_count: int):
    answer_like_manager.publish_new_like(
        answer_id=answer_id, new_vote_count=new_vote_count
    )


@app.task(ignore_result=True)
def publish_answer_correct(*, answer_id: int):
    answer_correct_manager.publish_correct(answer_id=answer_id)
