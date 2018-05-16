import uuid
from unittest import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from map.models import Coordinates
from mobile_res.models import MobileUser, ThreatType, EmergencyType, Report
from mobile_res.utils import random_username
from web.settings import REST_FRAMEWORK, HASH_CLASS
from web.utils import easy_post, easy_get
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
        cls.reports_limit_rate = int(REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['reports'].split("/")[0])
        cls.events_limit_rate = int(REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['events'].split("/")[0])
        cls.anon_limit_rate = int(REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon'].split("/")[0])

        cls.mobile_user = MobileUser.objects.create_random_mobile_user()
        cls.web_user = WebUser.objects.create_web_user(random_username())

    def test_report_throttle(self):
        # mobile token case
        report_url = reverse('mobile_res:report-list')
        for i in range(self.reports_limit_rate):
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
        report = Report.objects.create(coordinates=Coordinates.objects.create(
            latitude=10,
            longitude=22
        )
        )
        threat_url = reverse('mobile_res:threatreport-list')
        emergency_url = reverse('mobile_res:emergencyreport-list')

        for i in range(int(self.reports_limit_rate / 2)):
            t = ThreatType.objects.create(title=random_username())
            data = {'type': t.id, 'report': report.id}
            response = easy_post(self.client, threat_url, data, self.mobile_user.token.key)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for i in range(int(self.reports_limit_rate / 2)):
            e = EmergencyType.objects.create(title=random_username())
            data = {'type': e.id, 'report': report.id}
            response = easy_post(self.client, emergency_url, data, self.mobile_user.token.key)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        e = EmergencyType.objects.create(title='derrumbe total')
        data = {'type': e.id, 'report': report.id}
        response = easy_post(self.client, emergency_url, data, self.mobile_user.token.key)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        t = ThreatType.objects.create(title='grietas')
        data = {'type': t.id, 'report': report.id}
        response = easy_post(self.client, threat_url, data, self.mobile_user.token.key)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_web_resources_unlimit(self):
        reports_url = reverse('web_res:report-list')
        emergencies_url = reverse('web_res:emergencyreport-list')
        threat_url = reverse('web_res:threatreport-list')

        iter_limit = 500
        for i in range(iter_limit):
            response = easy_get(self.client, reports_url, {}, self.web_user.token.key)
            self.assertEqual(status.HTTP_200_OK, response.status_code)

        for i in range(iter_limit):
            response = easy_get(self.client, emergencies_url, {}, self.web_user.token.key)
            self.assertEqual(status.HTTP_200_OK, response.status_code)

        for i in range(iter_limit):
            response = easy_get(self.client, threat_url, {}, self.web_user.token.key)
            self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_anon_requests(self):
        create_nonce_url = reverse("mobile_res:nonce-list")
        challenge_url = reverse("mobile_res:challenge")

        res = self.client.post(create_nonce_url)
        self.assertEqual(status.HTTP_201_CREATED, res.status_code)
        nonce = res.data['key']
        challenge_response = HASH_CLASS(nonce.encode('utf-8')).hexdigest()
        res = self.client.post(challenge_url, {"h": challenge_response}, HTTP_AUTHORIZATION=nonce)
        self.assertEqual(status.HTTP_200_OK, res.status_code)

        for i in range(self.anon_limit_rate - 2):
            res = self.client.post(create_nonce_url)
            self.assertEqual(status.HTTP_201_CREATED, res.status_code)
            nonce = res.data['key']

        challenge_response = HASH_CLASS(nonce.encode('utf-8')).hexdigest()
        res = self.client.post(challenge_url, {"h": challenge_response}, HTTP_AUTHORIZATION=nonce)
        self.assertEqual(status.HTTP_429_TOO_MANY_REQUESTS, res.status_code)

        res = self.client.post(create_nonce_url)
        self.assertEqual(status.HTTP_429_TOO_MANY_REQUESTS, res.status_code)
