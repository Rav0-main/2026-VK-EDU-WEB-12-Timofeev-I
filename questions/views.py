from django.shortcuts import render
from dataclasses import dataclass
import django.http

from questions import pagination

@dataclass
class Question:
    id: str
    title: str
    text: str
    tags: list[str]
    answer_count: str
    vote_count: str

@dataclass
class Answer:
    text: str
    vote_count: str
    is_correct: bool

ANSWERS: dict[str, list[Answer]] = {
    "correct": [
        Answer("Correct #1", "34", True),
        Answer("Correct #2", "10", True),
        Answer("Correct #3", "5", True)
    ],
    "not_checked": [
        Answer("Not checked #1", "2", False),
        Answer("Not checked #2", "0", False),
        Answer("Not checked #3", "5", False),
        Answer("Not checked #4", "0", False)
    ]
}

QUESTIONS = [
    Question(
        id=f"{i}",
        title=f"Title #{i}",
        text=f"Question text #{i}",
        tags=[
            f"Tag_{j}" for j in range(1, (i+1) % 5 + 2)
        ],
        answer_count=f"{(i+ (i+1) % 7) % 15}",
        vote_count=f"{(i+ (i % 4) + 3) % 13}",
    )
    for i in range(0, 30)
]

def index(request: django.http.HttpRequest):
    page_number = pagination.get_page_number_from(request)

    page = pagination.get_page_of(QUESTIONS, page_number)

    return render(
        request,
        "questions/index.html",
        context={"questions": page.object_list, "page": page}
    )

def hot(request: django.http.HttpRequest):
    page_number = pagination.get_page_number_from(request)

    page = pagination.get_page_of(QUESTIONS[::-1], page_number)

    return render(
        request,
        "questions/hot.html",
        context={"questions": page.object_list, "page": page}
    )

def question(request: django.http.HttpRequest, number: int):
    question: Question = QUESTIONS[0]
    try:
        question = QUESTIONS[number]
    except IndexError:
        pass
    
    page_number = pagination.get_page_number_from(request)

    page = pagination.get_page_of(ANSWERS["correct"] + ANSWERS["not_checked"], page_number)
    answers_page: dict[str, list[Answer]] = {
        "correct": [obj for obj in page.object_list if obj.is_correct],
        "not_checked": [obj for obj in page.object_list if not obj.is_correct]
    }

    return render(
        request,
        "questions/answers.html",
        context={"question": question, "answers": answers_page, "page": page}
    )

def tag(request: django.http.HttpRequest, tag: str):
    tag = tag.lower()
    questions: list[Question] = [
        i for i in QUESTIONS if tag in map(lambda s: s.lower(), i.tags)
    ]

    page_number = pagination.get_page_number_from(request)

    page = pagination.get_page_of(questions, page_number)

    return render(
        request,
        "questions/tag.html",
        context={"questions": page.object_list, "page": page, "tag": tag}
    )
