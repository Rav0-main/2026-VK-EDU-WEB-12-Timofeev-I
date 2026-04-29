from django.urls import path
from questions import views

app_name: str = "questions"

urlpatterns = [
    path("", views.NewQuestionsView.as_view(), name="index"),
    path("hot", views.HotQuestionsView.as_view(), name="hot"),
    path("question/<int:question_id>", views.QuestionView.as_view(), name="question"),
    path("tag/<str:tag_name>", views.QuestionsByTagView.as_view(), name="tag"),
    path("ask", views.AskView.as_view(), name="ask")
]