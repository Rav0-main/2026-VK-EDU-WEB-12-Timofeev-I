from django.urls import path
from core import views

app_name: str = "core"

urlpatterns = [
    path("login", views.LoginView.as_view(), name="login"),
    path("signup", views.RegisterView.as_view(), name="register"),
    path("profile", views.ProfileView.as_view(), name="settings")
]