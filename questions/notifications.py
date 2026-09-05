from cent import Client, PublishRequest

class NotificationCentrifugeManager:
    def __init__(self, api_url: str, api_key: str, timeout: float = 2.5):
        self.__client = Client(api_url,api_key, timeout=timeout)

    def notificate(self, *, 
        question_author_id: int, question_id: int, answer_page: int,
        answer_id: int, author_nickname: str, message: str
        ):
        request_cent = PublishRequest(
            channel=f"notifications:user-{question_author_id}",
            data={
                "question_id": question_id,
                "answer_page": answer_page,
                "answer_id": answer_id,
                "author_nickname": author_nickname,
                "message": message
            }
        )
        
        self.__client.publish(request_cent)