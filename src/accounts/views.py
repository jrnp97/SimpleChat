from django.shortcuts import render
from django.conf import settings

from django.contrib import messages

from django.views.generic.edit import FormView

from accounts.forms import UserRegistrationForm


class RegistrationView(FormView):
    """ App View to handle user registration """
    http_method_names = [
        'get',
        'post',
    ]
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = settings.LOGIN_URL

    def form_invalid(self, form):
        return self.render_to_response(
            context=self.get_context_data(form=form),
            status=400,
        )

    def form_valid(self, form):
        if self.request.method == 'POST':
            _user = form.save(commit=True)
            messages.success(
                request=self.request,
                message=(f'User: {_user.username} '
                         f'was created successfully.'),
            )

        return super().form_valid(form=form)

