""" Module to define tests for chat views """

from urllib import parse as urlparse

from django.test import TestCase

from django.conf import settings

from django.contrib.auth import get_user_model

User = get_user_model()


class TestChatRoomView(TestCase):
    """ Class to define tests for chat.views.room_chat_view"""
    CHAT_ROOM_URI = '/chat/{room_name}/'

    def setUp(self):
        self.test_room_chat = self.CHAT_ROOM_URI.format(room_name='test')
        self.credentials = {
            'username': 'test_user',
            'password': 'test_pwd',
        }
        self.user = User.objects.create_user(
            **self.credentials
        )

    def test_view_only_should_support_get_method(self):
        """ uri should only support GET method """
        bad_method = [
            'post',
            'put',
            'delete',
            'options',
            'head',
        ]
        self.assertTrue(self.client.login(**self.credentials))
        for method in bad_method:
            response = getattr(self.client, method)(
                path=self.test_room_chat
            )
            self.assertEqual(
                405,
                response.status_code,
                msg=f'unexpected method handle {method}',
            )

    def test_view_only_should_response_for_authenticate_users(self):
        """ Test view only should response to authenticate users """
        response = self.client.get(path=self.test_room_chat)
        self.assertEqual(
            302,
            response.status_code,
            msg=u'must redirect to login page',
        )
        import pdb;pdb.set_trace()
        self.assertEqual(
            settings.LOGIN_URL,
            urlparse.urlsplit(response.url).path,
        )
        self.assertTrue(self.client.login(**self.credentials))
