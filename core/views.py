from typing import Any
from django.views.generic.base import TemplateView, View
from django import http
from django.contrib import auth
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

from core import forms
from core.mixins import CommonViewContextMixin, RedirectUrlValidatorMixin


class UserLoginView(CommonViewContextMixin, RedirectUrlValidatorMixin, View):
    template_name: str = "core/login.html"
    http_method_names = ["post", "get"]

    def post(self, request: http.HttpRequest):
        redirect_url = request.GET.get("next", reverse("core:login"))
        if not self.is_valid_redirect_url(request, redirect_url):
            return http.HttpResponseForbidden(b"Error. Wrong redirect url.")

        form = forms.UserLoginForm(request, request.POST)

        if form.is_valid():
            auth.login(request, form.auth_user)
            return http.HttpResponseRedirect(redirect_url)

        context = self.get_common_context(request)
        context["redirect_url"] = redirect_url
        context["form"] = form

        return render(request, self.template_name, context=context)
    
    def get(self, request: http.HttpRequest):
        redirect_url = request.GET.get("next", reverse("questions:index"))
        if not self.is_valid_redirect_url(request, redirect_url):
            return http.HttpResponseForbidden(b"Error. Wrong redirect url.")

        form = forms.UserLoginForm(request)

        context = self.get_common_context(request)

        context["redirect_url"] = redirect_url
        context["form"] = form

        return render(request, self.template_name, context=context)
    

class UserRegisterView(CommonViewContextMixin, View):
    template_name: str = "core/register.html"
    http_method_names = ["post", "get"]

    def post(self, request: http.HttpRequest):
        form = forms.UserRegisterForm(request, request.POST, request.FILES)

        if form.is_valid():
            user = form.save()
            auth.login(request, user)

            return http.HttpResponseRedirect(reverse("questions:index"))

        context = self.get_common_context(request)
        context["form"] = form

        return render(request, self.template_name, context=context)
    
    def get(self, request: http.HttpRequest):
        form = forms.UserRegisterForm(request)
        context = self.get_common_context(request)
        context["form"] = form

        return render(request, self.template_name, context=context)
       

class UserLogoutView(RedirectUrlValidatorMixin, View):
    http_method_names = ["post"]

    def post(self, request: http.HttpRequest):
        stay_on_url = request.GET.get("stay_on", reverse("questions:index"))

        if stay_on_url == "":
            stay_on_url = reverse("questions:index")

        if not self.is_valid_redirect_url(request, stay_on_url):
            return http.HttpResponseForbidden(b"Error. Wrong redirect url.")

        elif request.user.is_authenticated:
            auth.logout(request)

        return http.HttpResponseRedirect(stay_on_url)


class UserProfileView(LoginRequiredMixin, CommonViewContextMixin, View):
    template_name: str = "core/settings.html"
    login_url = reverse_lazy("core:login")

    def post(self, request: http.HttpRequest):
        context = self.get_common_context(request)
        form = forms.UserProfileForm(request, request.POST, request.FILES)
        context["form"] = form

        if form.is_valid():
            form.save()

        return render(request, self.template_name, context=context)

    def get(self, request: http.HttpRequest):
        context = self.get_common_context(request)
        form = forms.UserProfileForm(request)

        context["form"] = form

        return render(request, self.template_name, context=context)
    

class Http404View(CommonViewContextMixin, TemplateView):
    template_name = "404.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context |= self.get_common_context(self.request)

        return context
