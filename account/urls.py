from django.urls import path
from account import views

app_name: str = "account"

urlpatterns = [
    path("login", views.login, name="login"),
]