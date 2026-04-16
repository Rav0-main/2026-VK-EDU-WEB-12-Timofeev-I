from django.urls import path
from questions import views

app_name: str = "questions"

urlpatterns = [
    path("", views.index, name="index"),
    path("hot", views.hot, name="hot"),
    path("question/<int:number>", views.question, name="answers"),
    path("tag/<str:tag>", views.tag, name="tag"),
    path("ask", views.ask, name="ask")
]