from django.shortcuts import render
import django.http

from application import questions
from questions import pagination

def index(request: django.http.HttpRequest):
    page_number = pagination.get_page_number_from(request)

    page = pagination.get_page_of(questions.QUESTIONS, page_number)

    return render(
        request,
        "questions/index.html",
        context={
            "questions": page.object_list, "page": page,
            "logined": False,
            "popular_tags": questions.get_popular_tags(questions.QUESTIONS)
            }
    )

def hot(request: django.http.HttpRequest):
    page_number = pagination.get_page_number_from(request)

    page = pagination.get_page_of(questions.QUESTIONS[::-1], page_number)

    return render(
        request,
        "questions/hot.html",
        context={
            "questions": page.object_list, "page": page,
            "logined": False,
            "popular_tags": questions.get_popular_tags(questions.QUESTIONS)
            }
    )

def question(request: django.http.HttpRequest, number: int):
    question = questions.QUESTIONS[0]
    try:
        question = questions.QUESTIONS[number]
    except IndexError:
        pass
    
    page_number = pagination.get_page_number_from(request)

    page = pagination.get_page_of(questions.ANSWERS["correct"] + questions.ANSWERS["not_checked"], page_number)
    answers_page: dict[str, list[questions.Answer]] = {
        "correct": [obj for obj in page.object_list if obj.is_correct],
        "not_checked": [obj for obj in page.object_list if not obj.is_correct]
    }

    return render(
        request,
        "questions/answers.html",
        context={"question": question, "answers": answers_page, "page": page,
                 "logined": False,
                 "popular_tags": questions.get_popular_tags(questions.QUESTIONS)
                 }
    )

def tag(request: django.http.HttpRequest, tag: str):
    tag_lower = tag.lower()
    questions_with_tag: list[questions.Question] = [
        i for i in questions.QUESTIONS if tag_lower in map(lambda s: s.lower(), i.tags)
    ]

    page_number = pagination.get_page_number_from(request)

    page = pagination.get_page_of(questions_with_tag, page_number)

    return render(
        request,
        "questions/tag.html",
        context={"questions": page.object_list, "page": page, "tag": tag,
                 "logined": False,
                 "popular_tags": questions.get_popular_tags(questions.QUESTIONS)
                 }
    )

def ask(request: django.http.HttpRequest):
    return render(
        request, "questions/ask.html", context={
            "logined": True,
            "popular_tags": questions.get_popular_tags(questions.QUESTIONS)
        }
    )
