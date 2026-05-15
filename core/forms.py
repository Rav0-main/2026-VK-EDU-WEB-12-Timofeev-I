from django import forms
from django.contrib import auth
from django import http
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
from core.models import UserProfile
from core.mixins import UserFieldsPrepareMixin

class UserLoginForm(forms.Form, UserFieldsPrepareMixin):
    username = forms.CharField(max_length=127)
    password = forms.CharField(max_length=127, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.authenticated_user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        self.cleaned_data = super().clean()
        self.prepare_user_data(self.cleaned_data)

        self.authenticated_user = auth.authenticate(
            username=self.cleaned_data["username"], password=self.cleaned_data["password"]
        )

        if self.authenticated_user is None:
            raise forms.ValidationError("Error. Invalid login or password.")


class UserRegisterForm(forms.Form, UserFieldsPrepareMixin):
    username = forms.CharField(max_length=127)
    email = forms.EmailField(max_length=255)
    nickname = forms.CharField(max_length=127)
    password = forms.CharField(max_length=127, widget=forms.PasswordInput)
    password_confirmation = forms.CharField(max_length=127, widget=forms.PasswordInput)

    def clean(self):
        self.cleaned_data = super().clean()
        self.prepare_user_data(self.cleaned_data)

        if self.cleaned_data["username"] == "" or \
            self.cleaned_data["email"] == "" or \
            self.cleaned_data["password"] == "" or \
            self.cleaned_data["password_confirmation"] == "":
            raise forms.ValidationError("Error. You must be input data.")

        password_validation.validate_password(self.cleaned_data["password"], user=None)

        if self.cleaned_data["password"] != self.cleaned_data["password_confirmation"]:
            raise forms.ValidationError("Error. Passwords must be equals.")
        
        elif User.objects.filter(username=self.cleaned_data["username"]).first():
            raise forms.ValidationError("Error. User already exists.")
        
        return self.cleaned_data
        
    def save(self) -> User:
        registered_user = User.objects.create_user(
            username=self.cleaned_data["username"], email=self.cleaned_data["email"],
            password=self.cleaned_data["password"]
        )

        UserProfile.objects.create(user=registered_user, nickname=self.cleaned_data["nickname"])
        
        return registered_user
    

class UserProfileForm(forms.Form, UserFieldsPrepareMixin):
    username = forms.CharField(max_length=127)
    email = forms.EmailField(max_length=255)
    nickname = forms.CharField(max_length=127)

    def __init__(self, request: http.HttpRequest, *args, **kwargs):
        self.request = request

        super().__init__(*args, **kwargs)

        if request.method == "GET":
            if UserProfile.objects.filter(user=request.user).first() is None:
                self.data["nickname"] = ""
                self.data["username"] = request.user.username
                self.data["email"] = request.user.email

            else:
                try:
                    user = User.objects.prefetch_related("profile") \
                        .get(username=request.user.username)
        
                    self.data["username"] = user.username
                    self.data["nickname"] = user.profile.nickname
                    self.data["email"] = user.email

                except User.DoesNotExist:
                    self.data["username"] = ""
                    self.data["nickname"] = ""
                    self.data["email"] = ""

    def clean(self):
        if not self.request.user.is_authenticated:
            raise forms.ValidationError("Error. User must be authenticated.")

        self.cleaned_data = super().clean()
        self.prepare_user_data(self.cleaned_data)

        try:
            previous_nickname = UserProfile.objects.get(user=self.request.user).nickname

        except UserProfile.DoesNotExist:
            raise forms.ValidationError("Error. You must be have profile.")

        previous_username = self.request.user.username
        previos_email = self.request.user.email

        if previous_username == self.cleaned_data["username"] and \
            previous_nickname == self.cleaned_data["nickname"] and \
            previos_email == self.cleaned_data["email"]:
            raise forms.ValidationError("Error. You must be change fields.")
        
        elif self.cleaned_data["username"] == "" or \
            self.cleaned_data["email"] == "" or \
            self.cleaned_data["nickname"] == "":
            raise forms.ValidationError("Error. You must be input all fields.")

        elif self.cleaned_data["username"] != previous_username:
            exists_user = User.objects.filter(username=self.cleaned_data["username"]).first()

            if exists_user:
                raise forms.ValidationError("Error. User with new login already exists.")

        return self.cleaned_data
    
    def save(self):
        User.objects.filter(id=self.request.user.pk) \
            .update(username=self.cleaned_data["username"],
                    email=self.cleaned_data["email"])
        
        UserProfile.objects.filter(user=self.request.user) \
            .update(nickname=self.cleaned_data["nickname"])
    