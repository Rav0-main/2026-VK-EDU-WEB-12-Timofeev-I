from django import forms
from django.db import IntegrityError
from django import http
from questions.models.tag import TagContent, Tag
from questions.models.answer import Answer
from questions.models.question import Question

class AddAnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ["content"]

    def __init__(self, request: http.HttpRequest, question_id: int, *args, **kwargs):
        self.request = request
        self.question_id = question_id
        super().__init__(*args, **kwargs)

    def clean(self):
        self.question = Question.objects.filter(id=self.question_id).first()
        if self.question is None:
            raise forms.ValidationError("Вопрос не найден.")

        elif self.cleaned_data["content"] == "":
            raise forms.ValidationError("Вы должны ввести ответ.")

        if Answer.objects.filter(
                question=self.question, content=self.cleaned_data["content"],
                author=self.request.user
            ).first():
            raise forms.ValidationError("Вы также отвечали на этот вопрос ранее.")

        return self.cleaned_data

    def save(self, commit: bool = True):
        answer = Answer(
            question=self.question, content=self.cleaned_data["content"],
            author=self.request.user
        )

        if not commit:
            return answer

        try:
            answer.save()

        except IntegrityError:
            return Answer.objects.filter(
                question=self.question, content=self.cleaned_data["content"],
                author=self.request.user
            ).first()
        

class AskForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["title", "content"]

    tags = forms.CharField(max_length=255, widget=forms.Textarea)

    def __init__(self, request: http.HttpRequest, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if not self.request.user.is_authenticated or not self.request.user.is_active:
            raise forms.ValidationError("Вы должны быть авторизованы.")

        exist_question = Question.objects.filter(
            title=cleaned_data["title"], content=cleaned_data["content"]
        ).first()

        if exist_question is not None:
            raise forms.ValidationError("Такой вопрос уже существует")

        return cleaned_data

    def save(self, commit: bool = True):
        tags_list: set[str] = set(map(lambda s: s.lower(), self.cleaned_data["tags"].split()))

        exist_tags = TagContent.objects.filter(name__in=tags_list)
        exist_tag_names = set(tag.name for tag in exist_tags)

        try:
            question = Question.objects.create(
                title=self.cleaned_data["title"], content=self.cleaned_data["content"],
                author=self.request.user
            )
        except IntegrityError:
            return Question.objects.filter(
                title=self.cleaned_data["title"], content=self.cleaned_data["content"]
            ).first()
        

        Tag.objects.bulk_create(
            Tag(question=question, content=exist_tag) for exist_tag in exist_tags
        )

        tag_contents = TagContent.objects.bulk_create(
            TagContent(name=not_exist_tag) for not_exist_tag in tags_list.difference(exist_tag_names)
        )

        Tag.objects.bulk_create(
            Tag(question=question, content=tag_content) for tag_content in tag_contents
        )

        return question
