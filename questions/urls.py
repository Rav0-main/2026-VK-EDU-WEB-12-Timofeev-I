from django.urls import path
from questions import views

app_name: str = "questions"

urlpatterns = [
    path("", views.NewQuestionsView.as_view(), name="index"),
    path("hot", views.HotQuestionsView.as_view(), name="hot"),
    path("question/<int:question_id>", views.QuestionView.as_view(), name="question"),
    path("question/like/<int:question_id>", views.QuestionLikeAddView.as_view(), name="question_like_add"),
    path("answer/question/<int:question_id>", views.AnswerAddView.as_view(), name="add_answer"),
    path("answer/like/<int:answer_id>", views.AnswerLikeAddView.as_view(), name="answer_like_add"),
    path("tag/<str:tag_name>", views.QuestionsByTagView.as_view(), name="tag"),
    path("ask", views.AskView.as_view(), name="ask")
]
