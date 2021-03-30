""" Module to define accounts routes """

from django.urls import path

from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView

from accounts.views import RegistrationView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login_uri'),
    path('logout/', LogoutView.as_view(), name='logout_uri'),
    path('register/', RegistrationView.as_view(), name='registration_uri'),
    path(
        'profile/',
        login_required(
            TemplateView.as_view(template_name='accounts/profile.html')
        ),
        name='profile_uri',
    ),
]
