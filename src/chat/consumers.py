""" Module to define web-sockets consumers (handles) """
import json

from django.utils.datetime_safe import datetime

from channels.generic.websocket import AsyncWebsocketConsumer

from chat.tasks import stock_searching

from chat.constants import BOT_NAME

from chat.utils import is_stock_bot_message


class ChatConsumer(AsyncWebsocketConsumer):
    """ Async Chat Consumer to Manage WebSocket Logic. """

    async def connect(self):
        """ Override method to create room or join on it at websocket connection
         moment """
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.username = self.scope['user'].username
        self.room_group_name = 'room_chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, code):
        """ Override method to disconnect user from chat-room """
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    async def handle_bot_message(self, message):
        """ Method to manage how bot message is manage """
        stock_searching.delay(
            stock=message,
            room_name=self.room_group_name,
        )
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f'Hi {self.username}!, give a moment,'
                           f' I am looking the info for you!',
                'author': BOT_NAME,
            }
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if is_stock_bot_message(message):
            await self.handle_bot_message(message=message)
        else:
            # send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'author': self.username,
                }
            )

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message,
            'author': event['author'],
            'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        }))
