from django.urls import path
from core import views

app_name: str = "core"

urlpatterns = [
    path("login", views.UserLoginView.as_view(), name="login"),
    path("signup", views.UserRegisterView.as_view(), name="register"),
    path("profile", views.ProfileView.as_view(), name="settings"),
    path("logout", views.UserLogoutView.as_view(), name="logout")
]