""" Module to define tests for chat.utils """

from django.test import TestCase

import requests

from unittest.mock import Mock
from unittest.mock import patch

from chat import utils


class TestUtilities(TestCase):
    """ Testing chat utilities on chat.utils module """

    @patch.object(requests, 'request', side_effect=requests.ConnectionError)
    def test_request_with_retry_should_retry_request_on_max_retries(
            self,
            mocked_request
    ):
        """ Testing chat.utils.request_with_retry should do request as time as
        specified on max_retries param, and raise error if was not possible """
        max_retries = [
            1,
            2,
            3,
        ]
        for retries in max_retries:
            with self.assertRaises(requests.ConnectionError):
                utils.request_with_retry(
                    request_kwargs={
                        'method': 'GET',
                        'url': 'http://dummyserver.com',
                    },
                    max_retries=retries,
                    retry_delay=1,
                )
            self.assertEqual(retries, mocked_request.call_count)
            mocked_request.reset_mock()

    @patch.object(requests, 'request')
    def test_request_with_retry_should_retry_until_good_response(
            self,
            mocked_request
    ):
        """ Testing chat.utils.request_with_query should do requests
        until service response good """
        mock_response = Mock(content=b'data')
        mocked_request.side_effect = [requests.ConnectionError, mock_response]
        response = utils.request_with_retry(
            request_kwargs={
                'method': 'GET',
                'url': 'http://dummyserver.com',
            },
            max_retries=5,
            retry_delay=1,
        )
        self.assertEqual(2, mocked_request.call_count)
        self.assertEqual(b'data', response.content)

    @patch.object(requests, 'request')
    def test_request_with_retry_should_set_default_timeout_if_not_set(
            self,
            mocked_request
    ):
        """ Testing chat.utils.request_with_query should set default 300s
        of timeout if not specified """
        mock_response = Mock(content=b'data')
        mocked_request.return_value = mock_response
        data = {
            'method': 'GET',
            'url': 'http://dummyserver.com',
        }
        response = utils.request_with_retry(
            request_kwargs=data,
        )
        self.assertEqual(1, mocked_request.call_count)
        self.assertEqual(b'data', response.content)
        data['timeout'] = 300
        mocked_request.assert_called_with(**data)
        mocked_request.reset_mock()
        data['timeout'] = 10
        utils.request_with_retry(
            request_kwargs=data,
        )
        mocked_request.assert_called_with(**data)

    def test_is_bot_message_should_return_true_to_valid_messages(self):
        """ Testing chat.utils.is_stock_bot_message should return True
        if message has the next pattern `/stock=<stock_code>` """
        bad_msgs = [
            'stock=',
            '/stock',
        ]
        for msg in bad_msgs:
            self.assertFalse(
                utils.is_stock_bot_message(message=msg),
                msg=f'not handle value: {msg}'
            )
        bot_msgs = [
            '/stock=',
            '/stock=code_value',
            '/stock=coding.value',
            '/stock=coding_val',
        ]
        for msg in bot_msgs:
            self.assertTrue(
                utils.is_stock_bot_message(message=msg),
                msg=f'not handle value: {msg}'
            )

    def test_is_bot_message_should_be_case_sensitive(self):
        """ Testing chat.utils.is_stock_bot_message fnc to care about
        letter sensitive, that means /Stock= if different from /stock=
        """
        bad_stock = [
            'Stock',
            'STock',
            'STOck',
            'STOCk',
            'STOCK',
        ]
        for stock in bad_stock:
            self.assertFalse(
                utils.is_stock_bot_message(message=f'/{stock}=code_test'),
                msg=f'Bad value handling: {stock}'
            )
        self.assertTrue(
            utils.is_stock_bot_message(message='/stock=code_test')
        )
