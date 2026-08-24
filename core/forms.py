from django import forms
from django.contrib import auth
from django import http
from django.core.validators import FileExtensionValidator, BaseValidator
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
from django.db import IntegrityError

from core.models import UserProfile
from core.mixins import UserFieldsPrepareMixin


class UserLoginForm(forms.Form, UserFieldsPrepareMixin):
    username = forms.CharField(max_length=127)
    password = forms.CharField(max_length=127, widget=forms.PasswordInput)

    def __init__(self, request: http.HttpRequest, *args, **kwargs):
        self.authenticated_user = None
        self.request = request
        super().__init__(*args, **kwargs)

    def clean(self):
        if self.request.user.is_authenticated:
            raise forms.ValidationError("Вы уже авторизованы.")
        
        self.cleaned_data = super().clean()
        self.prepare_user_data(self.cleaned_data)

        if self.cleaned_data["username"] is None or \
            self.cleaned_data["password"] is None:
            raise forms.ValidationError("Вы должны заполнить все поля.")

        self.authenticated_user = auth.authenticate(
            username=self.cleaned_data["username"], password=self.cleaned_data["password"]
        )

        if self.authenticated_user is None:
            raise forms.ValidationError("Неверный логин или пароль.")


class ImageFileSizeValidator(BaseValidator):
    message = "Размер файла не должен превышать %(limit_value)s МБ."
    code = None

    def compare(self, image_file, max_size_mb: float) -> bool:
        return image_file and image_file.size > 1024 * 1024 * max_size_mb


class UserRegisterForm(forms.Form, UserFieldsPrepareMixin):
    username = forms.CharField(max_length=127)
    email = forms.EmailField(max_length=255)
    nickname = forms.CharField(max_length=127)
    password = forms.CharField(max_length=127, widget=forms.PasswordInput)
    password_confirmation = forms.CharField(max_length=127, widget=forms.PasswordInput)
    avatar = forms.ImageField(required=False)

    def __init__(self, request: http.HttpRequest, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)
        self.fields["avatar"].validators.extend([
            FileExtensionValidator(
                allowed_extensions=["png", "jpeg", "jpg"],
                message="Разрешены только PNG, JPEG, JPG файлы. Вы загрузили файл с расширением %(extension)s"
            ),
            ImageFileSizeValidator(
                limit_value=6.7
            )
        ])

    def clean(self):
        if self.request.user.is_authenticated and self.request.user.is_active:
            raise forms.ValidationError("Вы уже авторизованы.")

        self.cleaned_data = super().clean()
        self.prepare_user_data(self.cleaned_data)

        if self.cleaned_data["username"] == "" or \
            self.cleaned_data["email"] == "" or \
            self.cleaned_data["nickname"] == "" or \
            self.cleaned_data["password"] == "" or \
            self.cleaned_data["password_confirmation"] == "":
            raise forms.ValidationError("Вы должны заполнить все поля.")

        password_validation.validate_password(self.cleaned_data["password"], user=None)

        if self.cleaned_data["password"] != self.cleaned_data["password_confirmation"]:
            raise forms.ValidationError("Введенные пароли не совпадают.")
        
        elif User.objects.filter(username=self.cleaned_data["username"]).first() is not None:
            raise forms.ValidationError("Пользователь уже существует.")
        
        return self.cleaned_data
        
    def save(self) -> User:
        try:
            registered_user = User.objects.create_user(
                username=self.cleaned_data["username"], email=self.cleaned_data["email"],
                password=self.cleaned_data["password"]
            )

        except IntegrityError:
            registered_user = User.objects.filter(
                username=self.cleaned_data["username"], email=self.cleaned_data["email"],
                password=self.cleaned_data["password"]
            ).first()

        try:
            registered_user_profile = UserProfile.objects.create(
                    user=registered_user, nickname=self.cleaned_data["nickname"],
            )
            if self.cleaned_data.get("avatar"):
                registered_user_profile.avatar = self.cleaned_data["avatar"]
    
        
        except IntegrityError:
            ...

        return registered_user
    

class UserProfileForm(forms.Form, UserFieldsPrepareMixin):
    username = forms.CharField(max_length=127)
    email = forms.EmailField(max_length=255)
    nickname = forms.CharField(max_length=127)
    avatar = forms.ImageField(required=False)

    def __init__(self, request: http.HttpRequest, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

        self.fields["avatar"].validators.extend([
            FileExtensionValidator(
                allowed_extensions=["png", "jpeg", "jpg"],
                message="Разрешены только PNG, JPEG, JPG файлы. Вы загрузили файл с расширением %(extension)s"
            ),
            ImageFileSizeValidator(
                limit_value=6.7
            )
        ])

        if request.method == "GET":
            self.__init_cleaned_data()

    def __init_cleaned_data(self):
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        
        if user_profile is None:
            self.cleaned_data = {
                "username": self.request.user.username,
                "email": self.request.user.email,
                "nickname": "",
            }
        else:
            self.cleaned_data = {
                "username": self.request.user.username,
                "email": self.request.user.email,
                "nickname": user_profile.nickname,
            }

    def clean(self):
        cleaned_data = super().clean()
        
        if not self.request.user.is_authenticated:
            raise forms.ValidationError("Вы должны быть авторизованы.")

        username = cleaned_data.get("username", "")
        email = cleaned_data.get("email", "")
        nickname = cleaned_data.get("nickname", "")
        avatar = cleaned_data.get("avatar")

        if not username or not email or not nickname:
            raise forms.ValidationError("Вы должны заполнить все поля.")

        try:
            user_profile = UserProfile.objects.get(user=self.request.user)
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(user=self.request.user, nickname=self.request.user.username)

        previous_nickname = user_profile.nickname
        previous_username = self.request.user.username
        previous_email = self.request.user.email

        if  previous_username == username and \
            previous_nickname == nickname and \
            previous_email == email and \
            not avatar:
            raise forms.ValidationError("Вы должны изменить хотя бы одно поле или загрузить аватар.")
        
        if username != previous_username:
            exists_user = User.objects.filter(username=username).exclude(id=self.request.user.id).first()
            if exists_user:
                raise forms.ValidationError("Пользователь с таким логином уже существует.")

        cleaned_data = self.prepare_user_data(cleaned_data)
        return cleaned_data
    
    def save(self):
        cleaned_data = self.cleaned_data
        
        User.objects.filter(id=self.request.user.pk).update(
            username=cleaned_data["username"],
            email=cleaned_data["email"]
        )
        
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        
        if cleaned_data.get("avatar"):
            profile.avatar = cleaned_data["avatar"]
            profile.nickname = cleaned_data["nickname"]
        else:
            profile.nickname = cleaned_data["nickname"]
        
        profile.save()
