from django import forms
from django.contrib import auth
from django.contrib.auth.models import User
from core.models import UserProfile

class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=128)
    password = forms.CharField(max_length=128, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.authenticated_user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        username = self.cleaned_data["username"]
        password = self.cleaned_data["password"]

        self.authenticated_user = auth.authenticate(username=username, password=password)

        if self.authenticated_user is None:
            raise forms.ValidationError("Error. Invalid login or password.")


class UserRegisterForm(forms.Form):
    username = forms.CharField(max_length=128)
    email = forms.EmailField(max_length=256)
    nickname = forms.CharField(max_length=128)
    password = forms.CharField(max_length=128, widget=forms.PasswordInput)
    password_confirmation = forms.CharField(max_length=128, widget=forms.PasswordInput)

    def clean(self):
        if self.cleaned_data["username"] is None or \
            self.cleaned_data["email"] is None or \
            self.cleaned_data["password"] is None or \
            self.cleaned_data["password_confirmation"] is None:
            raise forms.ValidationError("Error. You must be input data.")
        
        elif self.cleaned_data["password"] != self.cleaned_data["password_confirmation"]:
            raise forms.ValidationError("Error. Passwords must be equals.")
        
        elif User.objects.filter(username=self.cleaned_data["username"]).first():
            raise forms.ValidationError("Error. User already exists.")
        
    def save(self) -> User:
        registered_user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"]
        )

        UserProfile.objects.create(user=registered_user, nickname=self.cleaned_data["nickname"])
        
        return registered_user
        
