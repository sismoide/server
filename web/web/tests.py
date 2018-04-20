import uuid
from unittest import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from mobile_res.models import MobileUser
from web_res.models import WebUser


class UserAccountTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.web_user = WebUser.objects.create_web_user('test_web_user', password='sut')
        cls.mobile_user = MobileUser.objects.create_random_mobile_user()

    def test_web_resource_protection(self):
        # reports
        url = reverse('web_res:report-list')
        # no token case
        response = self.client.get(url, format='json')
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

        # mobile token case
        response = self.client.get(url, format='json', HTTP_AUTHORIZATION="Token {}".format(self.mobile_user.token.key))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

        # web token case
        response = self.client.get(url, format='json', HTTP_AUTHORIZATION="Token {}".format(self.web_user.token.key))
        self.assertEqual(status.HTTP_200_OK, response.status_code)


class UuidTestCase(TestCase):
    def test_uuid1_unicity(self):
        iterations = 1000
        hexes = []

        for i in range(iterations):
            hexes.append(uuid.uuid1().hex)

        hexes_set = set(hexes)
        self.assertEqual(len(hexes), len(hexes_set))

    def test_uuid4_unicity(self):
        iterations = 1000
        hexes = []

        for i in range(iterations):
            hexes.append(uuid.uuid4().hex)

        hexes_set = set(hexes)
        self.assertEqual(len(hexes), len(hexes_set))
