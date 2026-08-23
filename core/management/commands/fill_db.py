from typing import Any

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandParser

from random import randint

from core.models import UserProfile
from questions.models import Question, Answer, Tag, TagContent, AnswerLike, QuestionLike
from questions.models._like_type import LikeType


USERS_LIST_LIMIT: int = 10 #can only <= 10 :(.


class UsersCreator:
    list_limit: int = USERS_LIST_LIMIT

    def create(self, count: int) -> tuple[list[User], list[UserProfile]]:
        if count > self.list_limit or count < 0:
            raise ValueError(f"Users count must be >= 0 and <= {self.list_limit}.")
        
        elif count == 0:
            return ([], [])

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

        return (
            [user[0] for user in users],
            [user[1] for user in users]
        )

    def __get_user(self, user_id: int) -> tuple[User, UserProfile]:
        user = User()

        user.first_name = f"FIRST_NAME_{user_id}"
        user.last_name = f"LAST_NAME_{user_id}"
        user.email = f"EMAIL_{user_id}@email.com"
        user.username = f"username_{user_id}"

        user_profile = UserProfile()
        user_profile.user = user
        user_profile.nickname = f"nickname_{user_id}"

        return (user, user_profile)
    

class QuestionsCreator:
    list_limit: int = 10 * USERS_LIST_LIMIT

    def create(self, users: list[User], questions_per_user: int) -> list[Question]:
        if len(users) == 0:
            return []
        
        elif len(users) * questions_per_user > self.list_limit or \
            questions_per_user < 0:
            raise ValueError(f"Questions count must be >= 0 and <= {self.list_limit}")
        
        elif questions_per_user == 0:
            return []

        questions = []
        for user in users:
            questions.extend(
                self.__get_questions(questions_per_user, user)
            )

        return questions

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
    list_limit: int = 100 * USERS_LIST_LIMIT

    def create(self, questions: list[Question], answer_authors: list[User]) -> list[Answer]:
        if len(questions) * len(answer_authors) == 0:
            return []

        elif len(answer_authors) * len(questions) > self.list_limit:
            raise ValueError(f"Answers count must be >= 0 and <= {self.list_limit}.")
        
        answers = []
        for question in questions:
            answers.extend(
                self.__get_answers(question, answer_authors)
            )

        return answers

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
    tag_contents_list_limit: int = USERS_LIST_LIMIT
    tags_list_limit: int = 100 * USERS_LIST_LIMIT

    def create_tag_contents(self, count: int) -> list[TagContent]:
        if count > self.tag_contents_list_limit or count < 0:
            raise ValueError(f"Tag contents count must be >= 0 and <= {self.tag_contents_list_limit}.")
        
        elif count == 0:
            return []

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

        return tag_contents
    
    def create_tags_to_questions(
            self, questions: list[Question], tag_contents: list[TagContent]
        ) -> list[Tag]:
        if len(questions) * len(tag_contents) == 0:
            return []
        
        tags = []
        for question in questions:
            tags.extend(
                Tag(
                    question=question,
                    content=tag_contents[i]
                )
                for i in range(randint(1, min(len(tag_contents), 4)))
            )
            
        return tags
    

class LikeCreator:
    list_limit: int = 200 * USERS_LIST_LIMIT

    def create_question_likes_to(
            self, questions: list[Question], users: list[User]
        ) -> list[QuestionLike]:
        if len(questions) * len(users) == 0:
            return []
        
        likes: list[QuestionLike] = []
        for question in questions:
            likes.extend(
                QuestionLike(
                    question=question,
                    author=users[i],
                    type=self.__rand_like_type()
                )
                for i in range(len(users))
            )

        return likes
    
    def create_answer_likes_to(
            self, answers: list[Answer], users: list[User]
        ) -> list[AnswerLike]:

        if len(answers) * len(users) == 0:
            return []
        
        likes: list[AnswerLike] = []
        for answer in answers:
            likes.extend(
                AnswerLike(
                    answer=answer,
                    author=users[i],
                    type=self.__rand_like_type()
                )
                for i in range(len(users))
            )

        return likes
        
    def __rand_like_type(self) -> LikeType:
        return 1 if randint(0, 1) == 1 else -1


class Command(BaseCommand):
    users_creator = UsersCreator()
    questions_creator = QuestionsCreator()
    answers_creator = AnswersCreator()
    tags_creator = TagCreator()
    likes_creator = LikeCreator()
    
    help = r"""
        Append in database:
        1) Users count = RATIO
        2) Questions count = RATIO * 10
        3) Answers count = RATIO * 100
        4) Different tags = RATIO
        5) User likes count:
            5.1) Question likes count = RATIO * 100
            5.2) Answer likes count = RATIO * 100
    """

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--ratio", dest="ratio", type=int, required=True)

    def handle(self, *args: Any, **options: Any) -> str | None:
        ratio = options["ratio"]

        if ratio % self.users_creator.list_limit != 0:
            self.__create_group(ratio % self.users_creator.list_limit)
            ratio -= ratio % self.users_creator.list_limit

        for i in range(self.users_creator.list_limit,
                       ratio+self.users_creator.list_limit,
                       self.users_creator.list_limit):
            self.__create_group(self.users_creator.list_limit)

    def __create_group(self, users_count: int):
        users, user_profiles = self.users_creator.create(users_count)
        questions = self.questions_creator.create(users, 10)
        answers = self.answers_creator.create(questions, users)
        tag_contents = self.tags_creator.create_tag_contents(users_count)
        tags = self.tags_creator.create_tags_to_questions(questions, tag_contents)
        question_likes = self.likes_creator.create_question_likes_to(questions, users)
        answer_likes = self.likes_creator.create_answer_likes_to(answers, users)

        User.objects.bulk_create(users)
        UserProfile.objects.bulk_create(user_profiles)
        Question.objects.bulk_create(questions)
        Answer.objects.bulk_create(answers)
        TagContent.objects.bulk_create(tag_contents)
        Tag.objects.bulk_create(tags)
        QuestionLike.objects.bulk_create(question_likes)
        AnswerLike.objects.bulk_create(answer_likes)
