import datetime as dt

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from mobile_res.models import EmergencyType, EmergencyReport
from mobile_res.models import Report, Coordinates
# Create your tests here.
from web_res.models import WebUser


class ReportTests(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # full coords
        cls.full_coord1 = Coordinates.objects.create(
            latitude=179.555555,
            longitude=122.123456,
            elevation=120.5
        )

        # partial coords
        cls.part_coord1 = Coordinates.objects.create(
            latitude=-179.555555,
            longitude=-122.123456
        )

        # reports
        cls.report1 = Report.objects.create(
            coordinates=cls.full_coord1,
            intensity=1,
            created_on=dt.datetime(1990, 8, 23, hour=13, minute=37)
        )
        cls.report2 = Report.objects.create(
            coordinates=cls.part_coord1,
            intensity=8,
            created_on=dt.datetime(2018, 10, 5, hour=12, minute=3)
        )

    # test that only the appropiate reports are sent when filtered by date
    def test_get_reports(self):
        url = reverse('web_res:report-list')
        data = {'start': '2018-01-01T00:00', 'end': '2018-12-31T00:00'}
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # test that end_date < start_date sends no reports
    def test_invalid_filter(self):
        url = reverse('web_res:report-list')
        data = {'start': '2018-01-01T00:00', 'end': '2017-01-01T00:00'}
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class EmergencyTests(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # full coords
        cls.full_coord1 = Coordinates.objects.create(
            latitude=179.555555,
            longitude=122.123456,
            elevation=120.5
        )

        # partial coords
        cls.part_coord1 = Coordinates.objects.create(
            latitude=-179.555555,
            longitude=-122.123456
        )

        # reports
        cls.report1 = Report.objects.create(
            coordinates=cls.full_coord1,
            intensity=1,
            created_on=dt.datetime(1990, 8, 23, hour=13, minute=37)
        )
        cls.report2 = Report.objects.create(
            coordinates=cls.part_coord1,
            intensity=8,
            created_on=dt.datetime(2018, 10, 5, hour=12, minute=3)
        )

        # emergency types
        cls.em_type1 = EmergencyType.objects.create(
            title="incendio"
        )
        cls.em_type2 = EmergencyType.objects.create(
            title="tsunami"
        )

        # emergency reports
        cls.em_report1 = EmergencyReport.objects.create(
            type=cls.em_type1,
            report=cls.report1
        )
        cls.em_report2 = EmergencyReport.objects.create(
            type=cls.em_type2,
            report=cls.report2
        )

    # test that only the appropiate reports are sent when filtered by date
    def test_get_reports(self):
        url = reverse('web_res:emergencyreport-list')
        data = {'start': '2018-01-01T00:00', 'end': '2018-12-31T00:00'}
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # test that end_date < start_date sends no reports
    def test_invalid_filter(self):
        url = reverse('web_res:emergencyreport-list')
        data = {'start': '2018-01-01T00:00', 'end': '2017-01-01T00:00'}
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class WebUserTest(APITestCase, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wu1 = WebUser.objects.create_web_user('juan', password='juanito_123')

    def test_creation(self):
        self.assertIsNotNone(WebUser.objects.get(user__username='juan'))
        self.assertIsNotNone(self.wu1.token)
        self.assertIsInstance(self.wu1.token, Token)

        du1 = User.objects.get(username='juan')
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username='pepito')
        self.assertFalse(du1.check_password('juan'))
        self.assertTrue(du1.check_password('juanito_123'))

        self.assertIsNotNone(du1)
        self.assertIsNotNone(du1.password)
        self.assertEqual("", du1.email)
        self.assertIsNotNone(self.wu1.token)

        du1.delete()
        with self.assertRaises(WebUser.DoesNotExist):
            WebUser.objects.get(user__username='juan')

    def test_modify_password(self):
        # probado a mano
        pass
