from django.test.testcases import TestCase
from rest_framework.test import APIClient
from django.urls.base import reverse

from ..api import ContentType


class APITestCase(TestCase):
    client_class = APIClient

    def post_json(self, url, data, content_type=ContentType.request_json):
        return self.client.post(path=url, data=data, content_type=content_type)
    # def create_user(self, username, password, admin_type=AdminType.REGULAR_USER, login=True,
    #                 problem_permission=ProblemPermission.NONE):
    #     user = User.objects.create(username=username, admin_type=admin_type, problem_permission=problem_permission)
    #     user.set_password(password)
    #     UserProfile.objects.create(user=user)
    #     user.save()
    #     if login:
    #         self.client.login(username=username, password=password)
    #     return user
    #
    # def create_admin(self, username="admin", password="admin", login=True):
    #     return self.create_user(username=username, password=password, admin_type=AdminType.ADMIN,
    #                             problem_permission=ProblemPermission.OWN,
    #                             login=login)
    #
    # def create_super_admin(self, username="root", password="root", login=True):
    #     return self.create_user(username=username, password=password, admin_type=AdminType.SUPER_ADMIN,
    #                             problem_permission=ProblemPermission.ALL, login=login)

    def reverse(self, url_name, *args, **kwargs):
        return reverse(url_name, *args, **kwargs)

    def assertSuccess(self, response):
        if not response.data["error"] is None:
            raise AssertionError("response with errors, response: " + str(response.data))

    def assertFailed(self, response, msg=None):
        self.assertTrue(response.data["error"] is not None)
        if msg:
            self.assertEqual(response.data["data"], msg)
