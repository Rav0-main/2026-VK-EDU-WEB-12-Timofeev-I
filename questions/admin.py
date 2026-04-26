from django.contrib import admin
from questions.models import Question, QuestionLike, Tag, Answer, AnswerLike

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = [
        "id", "author", "title", "content"
    ]


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = [
        "question__id", "author__id", "type"
    ]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = [
        "question__id", "title"
    ]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = [
        "question__id", "author__id", "content", "is_correct"
    ]

    
@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = [
        "answer__id", "author__id", "type"
    ]

"""
:)
from django.contrib import admin
from django.http import HttpRequest
from main.models import Chat, ChatMember, ChatMessage

# Register your models here.


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "view_type", "is_active"]
    readonly_fields = ["id", "view_type"]
    
    
    Критерий отображения.
    
    list_filter = ["is_active", "view_type"]

    class ChatMemberInline(admin.TabularInline):
        model = ChatMember
        raw_id_fields = ["user"]
        extra = 0
        fields = ["user"]

        def has_add_permission(self, request: HttpRequest, *args, **kwargs) -> bool:
            return False

    inlines = [ChatMemberInline]


@admin.register(ChatMember)
class ChatMemberAdmin(admin.ModelAdmin):
    
    Красивое отображение.
    
    list_display = ["id", "user", "chat"] # user.email = user__email

    
    Поиск по полям.
    
    search_fields = ["user__username", "user__email", "chat__title"]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    ...
"""
