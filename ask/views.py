from django.shortcuts import render
import django.http

def ask(request: django.http.HttpRequest):
    return render(request, "ask/index.html", context={"logined": True})