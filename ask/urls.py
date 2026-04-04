from django.urls import path
from ask import views

app_name: str = "ask"

urlpatterns = [
    path("ask", views.ask, name="index"),
]