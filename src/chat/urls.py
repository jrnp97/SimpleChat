""" Module to define chat wsgi routers """

from django.urls import path

from chat.views import room_chat_view

app_name = 'chat'
urlpatterns = [
    path('<str:room_name>/', room_chat_view)
]
