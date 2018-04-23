import uuid
from unittest import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from mobile_res.models import MobileUser, Report, ThreatType, Coordinates, EmergencyType
from mobile_res.utils import random_username
from web.settings import REST_FRAMEWORK
from web.utils import easy_post
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


class ThrottleTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mobile_limit_rate = int(REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['mobile'].split("/")[0])

    def setUp(self):
        self.web_user = WebUser.objects.create_web_user(random_username())
        self.mobile_user = MobileUser.objects.create_random_mobile_user()

    def test_report_throttle(self):
        # mobile token case
        report_url = reverse('mobile_res:report-list')
        for i in range(self.mobile_limit_rate):
            # all of theese should pass correct
            data = {'coordinates': {'latitude': 10, 'longitude': 14}}
            response = easy_post(self.client, report_url, data, self.mobile_user.token.key)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # this one should fail
        data = {'coordinates': {'latitude': 10, 'longitude': 14}}
        response = easy_post(self.client, report_url, data, self.mobile_user.token.key)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_threat_throttle(self):
        # create a report
        self.mobile_user = MobileUser.objects.create_random_mobile_user()
        self.mobile_user = MobileUser.objects.create_random_mobile_user()

        report = Report.objects.create(coordinates=Coordinates.objects.create(
            latitude=10,
            longitude=22
        )
        )
        threat_url = reverse('mobile_res:threatreport-list')

        for i in range(self.mobile_limit_rate):
            t = ThreatType.objects.create(title=random_username())
            data = {'type': t.id, 'report': report.id}
            response = easy_post(self.client, threat_url, data, self.mobile_user.token.key)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        t = ThreatType.objects.create(title='grietas')
        data = {'type': t.id, 'report': report.id}
        response = easy_post(self.client, threat_url, data, self.mobile_user.token.key)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_emergency_throttle(self):
        # create a report
        self.mobile_user = MobileUser.objects.create_random_mobile_user()

        report = Report.objects.create(coordinates=Coordinates.objects.create(
            latitude=10,
            longitude=22
        )
        )
        emergency_url = reverse('mobile_res:emergencyreport-list')

        for i in range(self.mobile_limit_rate):
            e = EmergencyType.objects.create(title=random_username())
            data = {'type': e.id, 'report': report.id}
            response = easy_post(self.client, emergency_url, data, self.mobile_user.token.key)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        e = EmergencyType.objects.create(title='derrumbe total')
        data = {'type': e.id, 'report': report.id}
        response = easy_post(self.client, emergency_url, data, self.mobile_user.token.key)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    # todo: test anon request limit and web request no-limit
