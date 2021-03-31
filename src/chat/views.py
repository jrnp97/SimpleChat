""" Module to define chat wsgi views """
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET


@require_GET
@login_required
def room_chat_view(request, room_name):
    """ Simple Django-Function view to handle room chat rendering """
    return render(request, 'chat/chat_room.html', {'room_name': room_name})
