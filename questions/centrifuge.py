from cent import Client, PublishRequest, CentError
from application.config import ANSWERS_PER_PAGE


class NotificationCentrifugeManager:
    __slots__ = ["__client"]

    def __init__(self, api_url: str, api_key: str, timeout: float = 2.5):
        self.__client = Client(api_url, api_key, timeout=timeout)

    def notificate(
        self,
        *,
        question_author_id: int,
        answer_url: str,
        author_nickname: str,
        message: str,
    ) -> bool:
        request = PublishRequest(
            channel=f"notifications:users:{question_author_id}",
            data={
                "answer_url": answer_url,
                "author_nickname": author_nickname,
                "message": message,
            },
        )

        try:
            self.__client.publish(request)
            return True

        except CentError:
            return False


class AnswerCentrifugeManager:
    __slots__ = ["__client"]

    def __init__(self, api_url: str, api_key: str, timeout: float = 2.5):
        self.__client = Client(api_url, api_key, timeout=timeout)

    def publish_answer(
        self,
        *,
        question_id: int,
        answer_id: int,
        author_nickname: str,
        author_avatar_url: str,
        answer_vote_count: int,
        question_url: str,
        answer_index: int,
        content: str,
    ) -> bool:
        request = PublishRequest(
            channel=f"questions:{question_id}:answer",
            data={
                "answer_id": answer_id,
                "question_url": question_url,
                "answer_index": answer_index,
                "answers_on_page": ANSWERS_PER_PAGE,
                "author_nickname": author_nickname,
                "author_avatar_url": author_avatar_url,
                "answer_vote_count": answer_vote_count,
                "content": content,
            },
        )

        try:
            self.__client.publish(request)
            return True

        except CentError:
            return False
