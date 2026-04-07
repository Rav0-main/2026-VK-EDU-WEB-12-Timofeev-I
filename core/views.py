from django.shortcuts import render
import django.http

from application import questions

def login(request: django.http.HttpRequest):
    return render(
        request, "core/login.html", context={
            "logined": False,
            "popular_tags": questions.get_popular_tags(questions.QUESTIONS)
        }
    )

def register(request: django.http.HttpRequest):
    return render(
        request, "core/register.html", context={
            "logined": False,
            "popular_tags": questions.get_popular_tags(questions.QUESTIONS)
        }
    )

def profile(request: django.http.HttpRequest):
    return render(
        request, "core/settings.html", context={
            "logined": True,
            "popular_tags": questions.get_popular_tags(questions.QUESTIONS)
        }
    )