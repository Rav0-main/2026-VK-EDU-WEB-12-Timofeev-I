from typing import Any
from django.views.generic.base import TemplateView, View
from django import http
from django.contrib import auth
from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

from core import forms
from core.mixins import CommonViewContextMixin


class UserLoginView(CommonViewContextMixin, View):
    template_name: str = "core/login.html"
    http_method_names = ["post", "get"]

    def post(self, request: http.HttpRequest):
        #add valid on open redirect
        redirect_url = request.GET.get("next", reverse("core:login"))
        form = forms.UserLoginForm(request.POST)

        context = self.get_common_context_data(request)
        context["redirect_url"] = redirect_url
        context["form"] = form

        if form.is_valid() and request.user.is_anonymous:
            auth.login(request, form.authenticated_user)
            return http.HttpResponseRedirect(redirect_url)

        return render(request, self.template_name, context=context)
    
    def get(self, request: http.HttpRequest):
        redirect_url = request.GET.get("next", reverse("questions:index"))
        form = forms.UserLoginForm(request.POST)

        context = self.get_common_context_data(request)

        context["redirect_url"] = redirect_url
        context["form"] = form
        context["current_url"] = request.path

        return render(request, self.template_name, context=context)
    

class UserRegisterView(CommonViewContextMixin, View):
    template_name: str = "core/register.html"
    http_method_names = ["post", "get"]

    def post(self, request: http.HttpRequest):
        form = forms.UserRegisterForm(request.POST)

        context = self.get_common_context_data(request)

        if form.is_valid():
            registered_user = form.save()
            auth.login(request, registered_user)

            return http.HttpResponseRedirect(reverse("questions:index"))
        
        context["form"] = form

        return render(request, self.template_name, context=context)
    
    def get(self, request: http.HttpRequest):
        context = self.get_common_context_data(request)
        context["current_url"] = request.path

        return render(request, self.template_name, context=context)
       

class UserLogoutView(View):
    http_method_names = ["post"]

    def post(self, request: http.HttpRequest):
        stay_on_url = request.GET.get("stay_on", reverse("questions:index"))

        if stay_on_url == "":
            stay_on_url = reverse("questions:index")

        if request.user.is_authenticated:
            auth.logout(request)

        return http.HttpResponseRedirect(stay_on_url)


class ProfileView(LoginRequiredMixin, CommonViewContextMixin, View):
    template_name: str = "core/settings.html"
    login_url = reverse_lazy("core:login")

    def get(self, request: http.HttpRequest):
        context = self.get_common_context_data(request)

        user = User.objects.get(username=request.user.username) # can error
        context["user"] = user
        context["current_url"] = request.path

        return render(request, self.template_name, context=context)
    

class Http404View(CommonViewContextMixin, TemplateView):
    template_name = "404.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context |= self.get_common_context_data(self.request)

        return context
