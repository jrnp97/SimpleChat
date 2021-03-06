""" Module to define chat-utilities """
import re
import time
import requests

from asgiref.sync import async_to_sync

from django.utils.datetime_safe import datetime

from channels.layers import get_channel_layer

from chat.constants import BOT_NAME
from chat.constants import STOCK_MESSAGE_RGX


def request_with_retry(request_kwargs, retry_delay=10, max_retries=5):
    """
    Function to perform external services request with error handle and auto
    requests functionality.
    with a default timeout of 300 seconds (max. 5 min)
    Args:
        request_kwargs: A dictionary object defining request params (e. method)
        retry_delay: A integer number defining seconds to wait between retries.
        max_retries: A integer defining maximum requests retries to perform.
    """
    if 'timeout' not in request_kwargs:
        request_kwargs['timeout'] = 300
    retries = 0
    while retries < max_retries:
        try:
            return requests.request(
                **request_kwargs,
            )
        except (requests.ConnectionError, requests.ConnectTimeout):
            time.sleep(retry_delay)
            retries += 1
            if retries >= max_retries:
                raise


def is_stock_bot_message(message):
    """ Function to validate message is a valid stock_bot message
     Args:
         message: A string describing a message to validate.
    """
    # Match cause must be at the begin
    return bool(re.match(STOCK_MESSAGE_RGX, message))


# TODO: Test
def send_message_to_chat_room(msg, room_name, author=BOT_NAME):
    """ Function to send message to chat-room """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group=room_name,
        message={
            'type': 'chat_message',
            'message': msg,
            'author': author,
        }
    )
