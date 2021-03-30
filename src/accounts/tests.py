""" Module to define app tests """

from django.test import Client
from django.test import TestCase

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import is_password_usable

User = get_user_model()


class UserRegistrationTestCase(TestCase):
    """ Testing user registration flow """
    REGISTRATION_URI = '/accounts/register/'

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

    def tearDown(self):
        User.objects.all().delete()

    def test_registration_uri_should_only_support_post_method(self):
        """ Registration uri only must support POST HTTP-verb """
        bad_verbs = [
            'get',
            'head',
            'put',
            'options',
        ]
        for verb in bad_verbs:
            res = getattr(self.client, verb)(path=self.REGISTRATION_URI)
            self.assertEqual(res.status_code, 405)  # Method not allowed

    def test_registration_should_create_user_with_username_and_password(self):
        """ Registration process only need username, password and password
            confirmation to create a new user """
        form_data = {
            'username': 'test_user',
            'password': 'UltraSecretPassword',
            'password_confirmation': 'UltraSecretPassword',
        }
        self.assertFalse(
            User.objects.filter(username=form_data['username']).exists()
        )
        response = self.client.post(
            path=self.REGISTRATION_URI,
            data=form_data,
        )
        self.assertContains(
            response=response,
            text=f'User: {form_data["username"]} was created successfully.',
            status_code=201,  # Created
        )
        created_user = User.objects.get(username=form_data['username'])
        self.assertTrue(is_password_usable(created_user.password))
        self.assertTrue(created_user.active)
        self.assertFalse(created_user.is_superuser)
        self.assertFalse(created_user.is_staff)

    def test_registration_should_avoid_register_when_confirm_pwd_is_bad(self):
        """ Testing user registration should avoid create user if confirm
            password and password dont match """
        form_data = {
            'username': 'test_user',
            'password': 'UndetectablePWD',
            'confirm_password': 'undetectablePWD',
        }
        self.assertEqual(0, User.objects.count())
        response = self.client.post(
            path=self.REGISTRATION_URI,
            data=form_data,
        )
        self.assertContains(
            response=response,
            text='Password and Confirm Password Dont match.',
            status_code=400,  # Bad response
        )
        self.assertEqual(0, User.objects.count())

    def test_registration_should_avoid_register_when_username_was_taken(self):
        """ Testing user registration should avoid create a user when username
            exists on database. """
        usr = 'test_username'
        on_db = User.objects.create_user(
            username=usr,
            password=u'testing_testing',
        )
        form_data = {
            'username': usr,
            'password': 'UndetectablePWD',
            'confirm_password': 'UndetectablePWD',
        }
        response = self.client.post(
            path=self.REGISTRATION_URI,
            data=form_data,
        )
        self.assertContains(
            response=response,
            text='Username already exists on system.',
            status_code=400,  # Bad response
        )
        self.assertEqual(1, User.objects.count())
