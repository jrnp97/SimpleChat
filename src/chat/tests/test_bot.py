""" Module to including chat-testing """
import os

from django.test import TestCase

from django.conf import settings

from unittest.mock import Mock
from unittest.mock import patch

import requests

from chat.constants import STOCK_SERVICE_URL
from chat.constants import BOT_DEFAULT_ERROR_MSG

from chat.exceptions import BadFormatStockCsvException

TEST_DATA = os.path.join(
    os.path.dirname(__file__),
    'data'
)


@patch('chat.tasks.send_message_to_chat_room')
class BotStockCommandManagement(TestCase):
    """ Test case testing the components to handle
        /stock=<stock> command on a chat room, that are:
        * stock_command_task: A async celery tasks to look up stock information
        and send message back to chat-room
        * chat_room_web_socket: A Async WebSocket Consumer processing all chat
        message, and send stock command tasks to bot.
    """

    @property
    def stock_command_task(self):
        from chat.tasks import stock_searching
        return stock_searching

    @patch('chat.tasks.request_with_retry')
    def test_stock_command_task_should_send_failed_message_on_failure(
            self,
            mocked_request_util,
            mocked_send_message,
    ):
        """ Testing stock command should handle failure on logic and send a
        failure message to chat-room, possible known failures:
            * Bad external service response:
                - down service (connection error or timeout).
                - bad response.
            * Bad csv parsing processing:
                - unexpected format.
                - bad formatted file.
        for all errors the bot must send a standard message to chat-room:
            - "Unable to get stock information, please retry."
                (not report functionality)
        """
        chat_room = 'test_chat_room'
        side_effects = [
            requests.ConnectionError,
            requests.ConnectTimeout,
        ]
        for side_effect in side_effects:
            mocked_request_util.side_effect = side_effect
            with self.assertRaises(side_effect):
                self.stock_command_task.run(
                    stock='/stock=test_stock',
                    room_name=chat_room,
                )
            mocked_send_message.assert_called_with(
                msg=BOT_DEFAULT_ERROR_MSG,
                room_name=chat_room,
            )

        mocked_send_message.reset_mock()
        mocked_request_util.reset_mock()

        mock_response = Mock(content=b'')
        mocked_request_util.side_effect = None
        mocked_request_util.return_value = mock_response

        with self.assertRaises(BadFormatStockCsvException):
            self.stock_command_task.run(
                stock='/stock=test_stock',
                room_name='test_chat_room',
            )
        mocked_send_message.assert_called_with(
            msg=BOT_DEFAULT_ERROR_MSG,
            room_name=chat_room,
        )

    @patch('chat.tasks.request_with_retry')
    def test_stock_command_task_should_send_stock_info_formatted_to_chat(
            self,
            mocked_request_util,
            mocked_send_message,
    ):
        """ Testing stock command should stock message from csv file res """
        test_csv = os.path.join(TEST_DATA, 'aapl.us.csv')
        mock_response = Mock(content=open(test_csv, 'rb').read())
        mocked_request_util.return_value = mock_response
        expected_request_kwargs = {
            'method': 'GET',
            'url': STOCK_SERVICE_URL.format(stock_code='test_stock'),
        }
        self.stock_command_task.run(
            stock='/stock=test_stock',
            room_name='test_chat_room',
        )
        mocked_request_util.assert_called_with(
            request_kwargs=expected_request_kwargs,
        )
        mocked_send_message.assert_called_with(
            msg='AAPL.US quote is $120.11 per share',
            room_name='test_chat_room',
        )
