from django.urls import path
from core import views

app_name: str = "core"

urlpatterns = [
    path("login", views.login, name="login"),
    path("signup", views.register, name="register"),
    path("profile", views.profile, name="settings")
]