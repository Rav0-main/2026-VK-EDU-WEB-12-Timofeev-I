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
    username = forms.CharField(max_length=User._meta.get_field("username").max_length,
                               validators=User._meta.get_field("username").validators)

    password = forms.CharField(max_length=User._meta.get_field("password").max_length,
                               validators=User._meta.get_field("password").validators)
    
    def __init__(self, request: http.HttpRequest, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)
    
    def clean(self):
        if self.request.user.is_authenticated:
            raise forms.ValidationError("Вы уже авторизованы.")
        
        cleaned_data = super().clean()
        self.prepare_user_data(cleaned_data)

        if cleaned_data["username"] == "" or cleaned_data["password"] == "":
            raise forms.ValidationError("Заполните все поля.")
        
        self.auth_user = auth.authenticate(
            request=self.request,
            username=cleaned_data["username"],
            password=cleaned_data["password"]
        )
        
        if self.auth_user is None:
            raise forms.ValidationError("Неверный логин или пароль.")
        
        return cleaned_data
    
    def save(self, commit=True):
        raise NotImplementedError("Это форма входа, она не сохраняет пользователя.")


class ImageFileSizeValidator(BaseValidator):
    message = "Размер файла не должен превышать %(limit_value)s МБ."
    code = ""

    def compare(self, image_file, max_size_mb: float) -> bool:
        return image_file and image_file.size > 1024 * 1024 * max_size_mb


class UserRegisterForm(forms.ModelForm, UserFieldsPrepareMixin):
    class Meta:
        model = User
        fields = ["username", "email", "password"]

    nickname = forms.CharField(max_length=UserProfile._meta.get_field("nickname").max_length)

    password_confirmation = forms.CharField(max_length=User._meta.get_field("password").max_length,
                                            validators=User._meta.get_field("password").validators)
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
        if self.request.user.is_authenticated:
            raise forms.ValidationError("Вы уже авторизованы.")

        cleaned_data = super().clean()
        self.prepare_user_data(self.cleaned_data)

        if cleaned_data["username"] == "" or cleaned_data["email"] == "" or \
            cleaned_data["nickname"] == "" or cleaned_data["password"] == "" or \
            cleaned_data["password_confirmation"] == "":
            raise forms.ValidationError("Вы должны заполнить все поля.")

        password_validation.validate_password(cleaned_data["password"], user=None)

        if cleaned_data["password"] != cleaned_data["password_confirmation"]:
            raise forms.ValidationError("Введенные пароли не совпадают.")
        
        elif User.objects.filter(username=cleaned_data["username"]).first() is not None:
            raise forms.ValidationError("Пользователь с таким логином не может существовать.")
        
        return cleaned_data
        
    def save(self, commit: bool = True) -> User:
        try:
            user = User.objects.create_user(
                username=self.cleaned_data["username"], email=self.cleaned_data["email"],
                password=self.cleaned_data["password"]
            )

        except IntegrityError:
            user = User.objects.get(
                username=self.cleaned_data["username"], email=self.cleaned_data["email"],
                password=self.cleaned_data["password"]
            )

        try:
            user_profile = UserProfile.objects.create(
                    user=user, nickname=self.cleaned_data["nickname"],
            )
            if self.cleaned_data.get("avatar"):
                user_profile.avatar = self.cleaned_data["avatar"]
    
        
        except IntegrityError:
            ...

        return user
    
class UserProfileForm(forms.Form, UserFieldsPrepareMixin):
    username = forms.CharField(
        max_length=User._meta.get_field("username").max_length
    )
    
    email = forms.EmailField(
        max_length=User._meta.get_field("email").max_length,
        validators=User._meta.get_field("email").validators
    )

    nickname = forms.CharField(
        max_length=UserProfile._meta.get_field("nickname").max_length,
        validators=UserProfile._meta.get_field("nickname").validators
    )

    avatar = forms.FileField(
        required=False,
        validators=UserProfile._meta.get_field("avatar").validators
    )

    def __init__(self, request: http.HttpRequest, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

        self.fields["avatar"].validators.extend([
            FileExtensionValidator(
                allowed_extensions=["png", "jpeg", "jpg"],
                message="Разрешены только PNG, JPEG, JPG файлы."
            ),
            ImageFileSizeValidator(limit_value=6.7)
        ])

        if request.method and request.method.upper() == "GET":
            self.__set_initial_data()

    def __set_initial_data(self):
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        self.cleaned_data = {
            "username": self.request.user.username,
            "email": self.request.user.email,
            "nickname": user_profile.nickname if user_profile else "",
        }

    def clean(self):
        cleaned_data = super().clean()
        self.prepare_user_data(cleaned_data)

        username = cleaned_data.get("username", "")
        email = cleaned_data.get("email", "")
        nickname = cleaned_data.get("nickname", "")
        avatar = cleaned_data.get("avatar")

        if not username or not email or not nickname:
            print(cleaned_data)
            raise forms.ValidationError("Вы должны заполнить все поля.")

        has_changes = False
        
        if username != self.request.user.username:
            if User.objects.filter(username=username).exclude(id=self.request.user.pk).exists():
                raise forms.ValidationError("Пользователь с таким логином уже существует.")
            has_changes = True
        
        if email != self.request.user.email:
            has_changes = True
        
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        if user_profile and nickname != user_profile.nickname:
            has_changes = True
        
        if avatar:
            has_changes = True

        if not has_changes:
            raise forms.ValidationError("Вы должны изменить хотя бы одно поле или загрузить аватар.")

        return cleaned_data
    
    def save(self, commit: bool = True) -> User:
        user = self.request.user
        user.username = self.cleaned_data["username"]
        user.email = self.cleaned_data["email"]
        
        if commit:
            user.save()
        
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.nickname = self.cleaned_data["nickname"]
        
        if self.cleaned_data.get("avatar"):
            profile.avatar = self.cleaned_data["avatar"]
        
        if commit:
            profile.save()
        
        return user