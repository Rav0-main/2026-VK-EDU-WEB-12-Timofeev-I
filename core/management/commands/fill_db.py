from typing import Any, overload, Union
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandParser, CommandError
from random import randint

from core.models import UserProfile
from questions.models import Question, Answer, Tag, TagContent, AnswerLike, QuestionLike
from questions.models._like_type import LikeType

"""
СДЕЛАТЬ ТАК, ЧТОБЫ ДЛЯ БОЛЬШИХ RATIO ТОЖЕ РАБОТАЛО
"""

class UsersCreator:
    users_list_limit: int = 200

    def append_users(self, count: int):
        last_user = User.objects.all().order_by("-id").first()
        last_user_id: int = 0
        
        if last_user is not None:
            last_user_id = last_user.pk

        users: list[tuple[User, UserProfile]] = []
        
        for i in range(count):
            users.append(
                self.__get_user(last_user_id + 1)
            )

            last_user_id += 1
            
            if len(users) >= self.users_list_limit:
                User.objects.bulk_create(
                    user[0] for user in users
                )

                UserProfile.objects.bulk_create(
                    user[1] for user in users
                )

                users.clear()

        if users:
            User.objects.bulk_create(
                user[0] for user in users
            )

            UserProfile.objects.bulk_create(
                user[1] for user in users
            )

            users.clear()

    def __get_user(self, user_id: int) -> tuple[User, UserProfile]:
        user = User()

        user.first_name = f"FIRST_NAME_{user_id}"
        user.last_name = f"LAST_NAME_{user_id}"
        user.email = f"EMAIL_{user_id}@email.com"
        user.username = f"username_{user_id}"

        user_profile = UserProfile()
        user_profile.user = user
        user_profile.nickname = f"nickname_{user_id}"
        user_profile.avatar_path = f"path/to/avatar_{user_id}"

        return (user, user_profile)
    

class QuestionsCreator:
    questions_list_limit: int = 200
    def append_questions(self, users: list[User], questions_per_user: int):
        questions = []
        for user in users:
            questions.extend(
                self.__get_questions(questions_per_user, user)
            )

            if len(questions) >= self.questions_list_limit:
                Question.objects.bulk_create(questions)

                questions.clear()

        if questions:
            Question.objects.bulk_create(questions)

            questions.clear()

    def __get_questions(self, questions_per_user: int, user: User) -> list[Question]:
        return [
            Question(
                author=user,
                title=f"Title #{i+1}: @{user.username}",
                content=f"Question content #{i+1}: @{user.username}"
            )
            for i in range(questions_per_user)
        ]
    

class AnswersCreator:
    answers_list_limit: int = 200
    def append_answers(self, questions: list[Question], answer_authors: list[User]):
        answers = []
        for question in questions:
            answers.extend(
                self.__get_answers(question, answer_authors)
            )

            if len(answers) >= self.answers_list_limit:
                Answer.objects.bulk_create(
                    answers
                )

                answers.clear()

        if answers:
            Answer.objects.bulk_create(
                answers
            )

            answers.clear()

    def __get_answers(self, question: Question, authors: list[User]) -> list[Answer]:
        return [
            Answer(
                question=question,
                author=authors[i],
                content=f"Answer content #{i+1}: @{authors[i].username}",
                is_correct=self.__rand_answer_correct()
            )
            for i in range(len(authors))
        ]
    
    def __rand_answer_correct(self) -> bool:
        return bool(randint(0, 1))
    

class TagCreator:
    tag_contents_list_limit: int = 200
    tags_list_limit: int = 200

    def append_tag_contents(self, count: int):
        last_tag = TagContent.objects.all().order_by("-id").first()
        last_tag_id: int = 0

        if last_tag is not None:
            last_tag_id = last_tag.pk
        
        tag_contents = []
        for i in range(count):
            tag_contents.append(
                TagContent(
                    name=f"Tag {last_tag_id+1}"
                )
            )

            last_tag_id += 1
            if len(tag_contents) >= self.tag_contents_list_limit:
                TagContent.objects.bulk_create(
                    tag_contents
                )

                tag_contents.clear()

        if tag_contents:
            TagContent.objects.bulk_create(
                tag_contents
            )

            tag_contents.clear()

    def append_tags_to_questions(self, questions: list[Question], tag_contents: list[TagContent]):
        tags = []
        for question in questions:
            tags.extend(
                Tag(question=question, content=tag_contents[i])
                for i in range(randint(1, len(tag_contents)))
            )
            
            if len(tags) >= self.tags_list_limit:
                Tag.objects.bulk_create(
                    tags
                )

                tags.clear()

        if tags:
            Tag.objects.bulk_create(
                tags
            )

            tags.clear()


class LikeCreator:
    likes_list_limit: int = 200

    @overload
    def append_likes_to(self, like_owners: list[Question], users: list[User]) -> None:
        ...

    @overload
    def append_likes_to(self, like_owners: list[Answer], users: list[User]) -> None:
        ...

    def append_likes_to(self, like_owners: Union[list[Question], list[Answer]], users: list[User]) -> None:
        assert like_owners and users and \
            (isinstance(like_owners[0], Question) or isinstance(like_owners[0], Answer))

        is_question_likes = isinstance(like_owners[0], Question)
        likes = []
        for obj in like_owners:
            if is_question_likes:
                likes.extend(
                    QuestionLike(
                        question=obj,
                        author=users[i],
                        type=self.__rand_like_type()
                    )
                    for i in range(len(users))
                )
            else:
                likes.extend(
                    AnswerLike(
                        answer=obj,
                        author=users[i],
                        type=self.__rand_like_type()
                    )
                    for i in range(len(users))
                )

            if len(likes) >= self.likes_list_limit:
                if is_question_likes:
                    QuestionLike.objects.bulk_create(
                        likes
                    )

                else:
                    AnswerLike.objects.bulk_create(
                        likes
                    )

                likes.clear()

        if likes:
            if is_question_likes:
                QuestionLike.objects.bulk_create(
                    likes
                )

            else:
                AnswerLike.objects.bulk_create(
                    likes
                )
        
    def __rand_like_type(self) -> LikeType:
        return "+" if randint(0, 1) == 1 else "-"

class Command(BaseCommand, UsersCreator, QuestionsCreator, AnswersCreator, TagCreator, LikeCreator):
    help = r"""
        Append in database:
        1) Users count = RATIO
        2) Questions count = RATIO * 10
        3) Answers count = RATIO * 100
        4) Different tags = RATIO
        5) User likes count:
            5.1) Question likes count = RATIO * 70
            5.2) Answer likes count = RATIO * 130
    """

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--ratio", dest="ratio", type=int, required=True)

    def handle(self, *args: Any, **options: Any) -> str | None:
        ratio = options["ratio"]

        if ratio > 5:
            raise CommandError("RATIO very large.")

        self.append_users(ratio)
        users = list(User.objects.all().order_by("-id")[0:ratio])
        
        self.append_questions(users, 10)
        questions = list(Question.objects.all().order_by("-id")[0:ratio*10])

        self.append_answers(questions, users)
        answers = list(Answer.objects.all().order_by("-id")[0:ratio**2 + ratio*10])

        self.append_tag_contents(ratio)
        tag_contents = list(TagContent.objects.all().order_by("-id")[0:ratio])

        self.append_tags_to_questions(questions, tag_contents)

        self.append_likes_to(questions, users)
        self.append_likes_to(answers, users)
