from django.urls import path
from questions import views

app_name: str = "questions"

urlpatterns = [
    path("", views.NewQuestionsView.as_view(), name="index"),
    path("hot", views.HotQuestionsView.as_view(), name="hot"),
    path("question/<int:number>", views.QuestionView.as_view(), name="answers"),
    path("tag/<str:tag>", views.QuestionsByTagView.as_view(), name="tag"),
    path("ask", views.AskView.as_view(), name="ask")
]