from django.shortcuts import render
import django.http

def login(request: django.http.HttpRequest):
    return render(request, "core/login.html", context={"logined": False})

def register(request: django.http.HttpRequest):
    return render(request, "core/register.html", context={"logined": False})

def profile(request: django.http.HttpRequest):
    return render(request, "core/settings.html", context={"logined": True})