from django.shortcuts import render

from django.views.generic.edit import FormView


# Create your views here.

class RegistrationView(FormView):
    """ App View to handle user registration """

