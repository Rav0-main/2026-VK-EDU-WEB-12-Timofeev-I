from django.contrib import admin
from questions.models import Question, QuestionLike, Tag, Answer, AnswerLike


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = [
        "id", "author", "title", "content", "published_datetime"
    ]

    raw_id_fields = [
        "author"
    ]

    search_fields = [
        "author__username", "title", "content", "published_datetime"
    ]

    class QuestionAnswerInline(admin.TabularInline):
        model = Answer
        extra = 0

        raw_id_fields = [
            "author"
        ]

    inlines = [QuestionAnswerInline]


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = [
        "id", "question", "author", "type"
    ]

    raw_id_fields = [
        "question", "author"
    ]

    search_fields = [
        "question", "author"
    ]

    list_filter = [
        "type"
    ]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = [
        "id", "question", "name"
    ]

    raw_id_fields = [
        "question"
    ]

    search_fields = [
        "iname"
    ]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = [
       "id", "question", "author", "content", "is_correct"
    ]

    raw_id_fields = [
        "question", "author"
    ]

    search_fields = [
        "question", "author", "content"
    ]

    list_filter = [
        "is_correct"
    ]

    
@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = [
        "id", "answer", "author", "type"
    ]

    raw_id_fields = [
        "answer", "author"
    ]

    search_fields = [
        "answer", "author"
    ]

    list_filter = [
        "type"
    ]
