""" Module to define admin models behavior for accounts app """
from django.contrib import admin

from accounts.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """ Class to register User model on Admin """
