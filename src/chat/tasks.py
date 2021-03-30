""" Module to define chat-bot related command processing """
import re
import os
import csv
import sys
import uuid
import tempfile

from requests.exceptions import HTTPError
from requests.exceptions import ConnectTimeout
from requests.exceptions import ConnectionError

from chatApp import celery_app as app

from chat.exceptions import BadFormatStockCsvException

from chat.constants import STOCK_SERVICE_URL
from chat.constants import STOCK_MESSAGE_RGX
from chat.constants import BOT_DEFAULT_ERROR_MSG

from chat.utils import request_with_retry
from chat.utils import send_message_to_chat_room


@app.task
def stock_searching(stock, room_name):
    """ Task to perform stock info search """
    try:
        stock_code = re.match(STOCK_MESSAGE_RGX, stock).group('stock_code')
        if not stock_code.strip():
            raise ValueError('invalid stock code')
    except (AttributeError, ValueError):
        send_message_to_chat_room(
            msg=BOT_DEFAULT_ERROR_MSG,
            room_name=room_name,
        )
        raise
    try:
        response = request_with_retry(
            request_kwargs={
                'url': STOCK_SERVICE_URL.format(stock_code=stock_code),
                'method': 'GET',
            }
        )

        response.raise_for_status()
    except (HTTPError, ConnectionError, ConnectTimeout):
        send_message_to_chat_room(
            msg=BOT_DEFAULT_ERROR_MSG,
            room_name=room_name,
        )
        raise

    file_path = os.path.join(tempfile.gettempdir(), uuid.uuid4().hex)
    try:
        open(file_path, 'wb').write(response.content)

        with open(file_path, newline='') as csv_file:
            file_data = csv.DictReader(csv_file)
            row = next(file_data)
        send_message_to_chat_room(
            msg=f'{row["Symbol"]} quote is ${row["Open"]} per share',
            room_name=room_name,
        )
    except Exception as _:
        e_type, exc, tb = sys.exc_info()
        send_message_to_chat_room(
            msg=BOT_DEFAULT_ERROR_MSG,
            room_name=room_name,
        )
        raise BadFormatStockCsvException(f'unable to read file: {e_type}')
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
