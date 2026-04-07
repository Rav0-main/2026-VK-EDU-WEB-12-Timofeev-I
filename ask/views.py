from django.shortcuts import render
import django.http

from application import questions

def ask(request: django.http.HttpRequest):
    return render(
        request, "ask/index.html", context={
            "logined": True,
            "popular_tags": questions.get_popular_tags(questions.QUESTIONS)
        }
    )