from django.urls import path
from questions import views

app_name: str = "questions"

urlpatterns = [
    path("", views.NewQuestionsView.as_view(), name="index"),
    path("hot", views.HotQuestionsView.as_view(), name="hot"),
    path("questions/<int:question_id>", views.QuestionView.as_view(), name="question"),
    path("questions/<int:question_id>/like", views.QuestionLikeAddView.as_view(), name="question_like_add"),
    path("questions/<int:question_id>/answers", views.AnswerAddView.as_view(), name="answer_add"),
    path("answers/<int:answer_id>/like", views.AnswerLikeAddView.as_view(), name="answer_like_add"),
    path("answers/<int:answer_id>/set-correct", views.AnswerSetCorrectView.as_view(), name="answer_set_correct"),
    path("tag/<str:tag_name>", views.QuestionsByTagView.as_view(), name="tag"),
    path("ask", views.AskView.as_view(), name="ask")
]
