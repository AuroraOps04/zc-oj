import time

from rest_framework.test import APIClient

from utils.api.tests import APITestCase
from utils.shortcuts import rand_str
from .models import User


class CaptchaTest(APITestCase):
    client_class = APIClient

    def _set_captcha(self, session):
        captcha = rand_str(4)
        session["_django_captcha_key"] = captcha
        session["_django_captcha_expires_time"] = int(time.time()) + 30
        session.save()
        return captcha


class UserRegisterAPITestCase(CaptchaTest):
    def setUp(self) -> None:
        self.captcha = self._set_captcha(self.client.session)
        self.data = {
            'username': 'username',
            'password': 'password',
            'email': 'email@test.com',
            'captcha': self.captcha,
        }
        self.register_url = self.reverse('user_register_api')

    def set_captcha(self):
        self.data['captcha'] = self._set_captcha(self.client.session)

    def test_invalid_captcha(self):
        invalid_captcha = '****'
        self.data['captcha'] = invalid_captcha
        res = self.post_json(self.register_url, data=self.data)

        self.assertDictEqual(res.data, {'error': 'error', 'data': 'Invalid captcha'})

    def test_register_with_correct_info(self):
        response = self.post_json(self.register_url, data=self.data)
        self.assertDictEqual(response.data, {"error": '', "data": "Succeeded"})

    # def test_email_already_exists(self):
    #     self.test_register_with_correct_info()
    #     self.set_captcha()
    #     data = self.data
    #     data['username'] = 'non-exists_username'
    #     print(data)
    #     response = self.post_json(self.register_url, data=data)
    #     self.assertDictEqual(response.data, {'error': 'error', 'data': 'Email already exists'})

    def test_username_already_exists(self):
        self.test_register_with_correct_info()
        self.set_captcha()
        data = self.data
        data['email'] = 'not_validate@validate.com'
        response = self.post_json(self.register_url, data=data)
        self.assertDictEqual(response.data, {'error': 'error', 'data': 'Username already exists'})


class UserLoginAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.login_url = self.reverse('user_login_api')
        self.exists_data = {
            'username': 'taorui',
            'password': 'taorui..',
        }
        self.non_exists_data = {
            'username': 'non-exists_user',
            'password': 'non-exists_password',
        }
        self.disabled_data = {
            'username': 'disabled',
            'password': 'disabled',
        }
        user = User.objects.create(username='taorui', email='taorui@taorui.com')
        user.set_password('taorui..')
        user.save()
        user = User.objects.create(username='disabled', email='disbaled@taorui.com')
        user.set_password('disabled')
        user.is_disabled = True
        user.save()

    def test_exists_user_login(self):
        res = self.post_json(self.login_url, data=self.exists_data)
        self.assertDictEqual(res.data, {'error': '', 'data': 'Succeeded'})

    def test_non_exists_user_login(self):
        res = self.post_json(self.login_url, self.non_exists_data)
        self.assertDictEqual(res.data, {'error': 'error', 'data': 'Invalid account or password'})

    def test_disabled_user_login(self):
        res = self.post_json(self.login_url, self.disabled_data)
        self.assertDictEqual(res.data, {'error': 'error', 'data': 'Your account is disabled'})