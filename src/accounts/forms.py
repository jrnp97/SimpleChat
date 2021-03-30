""" Module to define accounts forms """

from django import forms

from accounts.models import User


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            'username',
            'password',
        ]

    def clean_username(self):
        username = self.cleaned_data['username']
        username = username.strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                'Username already exists on system.',
            )
        return username

    def clean(self):
        clean_data = super().clean()
        if clean_data.get('confirm_password') != clean_data.get('password'):
            raise forms.ValidationError(
                'Password and Confirm Password Dont match.'
            )
        return clean_data

    def save(self, commit=True):
        if not commit:
            return super(UserRegistrationForm, self).save(commit=commit)
        instance = super().save(commit=False)
        self.instance = User.objects.create_user(
            username=instance.username,
            password=instance.password,
        )
        return self.instance
