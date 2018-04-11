import datetime

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db import transaction
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from mobile_res.models import Coordinates, Report, IntensityQuestion, EmergencyType, ThreatType, ThreatReport, \
    EmergencyReport


class ModelsTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # fully defined coords
        cls.full_coord1 = Coordinates.objects.create(
            latitude=-179.555555,
            longitude=-122.123456,
            elevation=8000
        )
        cls.full_coord2 = Coordinates.objects.create(
            latitude=179.555555,
            longitude=122.123456,
            elevation=120.5
        )
        cls.full_coord3 = Coordinates.objects.create(
            latitude=-179.555555,
            longitude=122.123456,
            elevation=-100.333333333
        )
        cls.full_coord4 = Coordinates.objects.create(
            latitude=-2,
            longitude=5,
            elevation=0
        )

        # parcially defined coords
        cls.parc_coord1 = Coordinates.objects.create(
            latitude=-179.555555,
            longitude=-122.123456
        )
        cls.parc_coord2 = Coordinates.objects.create(
            latitude=179.555555,
            longitude=122.123456,
        )
        cls.parc_coord3 = Coordinates.objects.create(
            latitude=-179.555555,
            longitude=122.123456
        )
        cls.parc_coord4 = Coordinates.objects.create(
            latitude=-2,
            longitude=5
        )

        # reports
        cls.report1 = Report.objects.create(coordinates=cls.full_coord1,
                                            intensity=1)

        cls.report2 = Report.objects.create(coordinates=cls.parc_coord1,
                                            intensity=12)

        cls.report3 = Report.objects.create(coordinates=cls.parc_coord3,
                                            intensity=5)

        # questions
        cls.q4 = IntensityQuestion.objects.create(text="cuarta pregunta?", intensity=4)
        cls.q1 = IntensityQuestion.objects.create(text="primera pregunta?", intensity=1)
        cls.q3 = IntensityQuestion.objects.create(text="tercera pregunta?", intensity=3)
        cls.q2 = IntensityQuestion.objects.create(text="segunda pregunta?", intensity=2)

        # critic events
        cls.em_tsunami = EmergencyType.objects.create(title='Tsunami')
        cls.em_lahar = EmergencyType.objects.create(title='Lahar')

        cls.th_grietas = ThreatType.objects.create(title='Grietas en las estructuras')
        cls.th_humo = ThreatType.objects.create(title='Olor a humo')

    def test_complete_coords(self):
        # existence
        self.assertIsNotNone(self.full_coord1)
        self.assertIsNotNone(self.full_coord2)
        self.assertIsNotNone(self.full_coord3)
        self.assertIsNotNone(self.full_coord4)

        # lat
        self.assertLess(self.full_coord1.latitude, 0)
        self.assertGreater(self.full_coord2.latitude, 0)
        self.assertLess(self.full_coord3.latitude, 0)
        self.assertLess(self.full_coord4.latitude, 0)

        # elev
        self.assertGreater(self.full_coord1.elevation, 0)
        self.assertGreater(self.full_coord2.elevation, 0)
        self.assertLess(self.full_coord3.elevation, 0)
        self.assertEqual(self.full_coord4.elevation, 0)

        # long
        self.assertLess(self.full_coord1.longitude, 0)
        self.assertGreater(self.full_coord2.longitude, 0)
        self.assertGreater(self.full_coord3.longitude, 0)
        self.assertGreater(self.full_coord4.longitude, 0)

        # str
        self.assertTrue(str(self.full_coord1.elevation) in str(self.full_coord1))
        self.assertTrue("m" in str(self.full_coord1))

    def test_incomplete_coords(self):
        # existence
        self.assertIsNotNone(self.parc_coord1)
        self.assertIsNotNone(self.parc_coord2)
        self.assertIsNotNone(self.parc_coord3)
        self.assertIsNotNone(self.parc_coord4)

        # lat
        self.assertLess(self.parc_coord1.latitude, 0)
        self.assertGreater(self.parc_coord2.latitude, 0)
        self.assertLess(self.parc_coord3.latitude, 0)
        self.assertLess(self.parc_coord4.latitude, 0)

        # elev
        self.assertIsNone(self.parc_coord1.elevation)
        self.assertIsNone(self.parc_coord2.elevation)
        self.assertIsNone(self.parc_coord3.elevation)
        self.assertIsNone(self.parc_coord4.elevation)

        # long
        self.assertLess(self.parc_coord1.longitude, 0)
        self.assertGreater(self.parc_coord2.longitude, 0)
        self.assertGreater(self.parc_coord3.longitude, 0)
        self.assertGreater(self.parc_coord4.longitude, 0)

        # str
        self.assertTrue('m' not in str(self.parc_coord1))

    def test_reports(self):
        self.assertIsNotNone(self.report1)
        self.assertIsNotNone(self.report2)

        with self.assertRaises(ValidationError):
            Report.objects.create(coordinates=self.full_coord1, intensity=-1)
            Report.objects.create(coordinates=self.full_coord1, intensity=13)
            Report.objects.create(coordinates=self.full_coord1, intensity=-10)

        Report.objects.create(coordinates=self.full_coord1)
        self.assertIsNotNone(self.report1.created_on)
        self.assertIsNotNone(self.report2.created_on)
        self.assertIsNotNone(self.report1.modified_on)
        self.assertIsNotNone(self.report2.modified_on)

        with self.assertRaises(ProtectedError):
            self.full_coord1.delete()
            self.parc_coord1.delete()

    def test_question(self):
        q0 = IntensityQuestion.objects.create(text='pregunta 0', intensity=0)
        questions = IntensityQuestion.objects.all()  # should be gathered in order

        self.assertEqual(questions[3], self.q3)
        self.assertEqual(questions[2], self.q2)
        self.assertEqual(questions[0], q0)
        self.assertEqual(questions[1], self.q1)
        self.assertEqual(questions[4], self.q4)

        with self.assertRaises(IntegrityError):
            # add question in same position
            IntensityQuestion.objects.create(text='other question 1', intensity=1)
            IntensityQuestion.objects.create(text='primera pregunta?', intensity=999)

    def test_threat(self):
        ThreatReport.objects.create(
            type=self.th_humo,
            report=self.report1
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ThreatReport.objects.create(type=self.th_humo,
                                            report=self.report1)

        ThreatReport.objects.create(
            type=self.th_grietas,
            report=self.report1
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ThreatReport.objects.create(type=self.th_grietas,
                                            report=self.report1
                                            )
        with self.assertRaises(ValueError):
            with transaction.atomic():
                ThreatReport.objects.create(
                    type=self.em_lahar,
                    report=self.report1
                )

    def test_emergency(self):
        EmergencyReport.objects.create(
            type=self.em_lahar,
            report=self.report1
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                EmergencyReport.objects.create(
                    type=self.em_lahar,
                    report=self.report1)

        EmergencyReport.objects.create(
            type=self.em_tsunami,
            report=self.report1
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                EmergencyReport.objects.create(
                    type=self.em_tsunami,
                    report=self.report1
                )
        with self.assertRaises(ValueError):
            with transaction.atomic():
                EmergencyReport.objects.create(
                    type=self.th_humo,
                    report=self.report1
                )


class APIResourceTestCase(APITestCase):
    def test_partial_report(self):
        """
        Ensure that can create and patch a report
        :return:
        """

        post_url = reverse('mobile_res:report-list')

        # partial data
        data = {'coordinates': {'latitude': 10, 'longitude': 14}}
        response = self.client.post(post_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Report.objects.count(), 1)

        # test data integrity
        rep = Report.objects.all()[0]
        self.assertIsNone(rep.intensity)
        self.assertIsNotNone(rep.created_on)
        self.assertIsNotNone(rep.modified_on)
        # self.assertEqual(rep.created_on, rep.modified_on)
        past_modified_on = rep.modified_on
        past_created_on = rep.created_on

        self.assertIsNotNone(rep.coordinates)
        self.assertEqual(rep.coordinates.latitude, 10)
        self.assertEqual(rep.coordinates.longitude, 14)
        self.assertEqual(rep.created_on.second, rep.modified_on.second)
        self.assertIsNone(rep.coordinates.elevation)
        self.assertIsNotNone(rep.modified_on)
        self.assertNotEqual(rep.created_on, rep.modified_on)

        # suppose now i have the intensity
        report_id = response.data['id']
        patch_url = reverse('mobile_res:report-detail', kwargs={'pk': report_id})
        data = {'intensity': 4}
        response = self.client.patch(patch_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Report.objects.count(), 1)

        # test data integrity
        rep = Report.objects.all()[0]
        self.assertNotEqual(rep.created_on, rep.modified_on)
        self.assertEqual(rep.created_on, past_created_on)
        self.assertNotEqual(rep.modified_on, past_modified_on)
        self.assertEqual(rep.intensity, 4)

        # also old data should stay
        self.assertIsNotNone(rep.coordinates)
        self.assertEqual(rep.coordinates.latitude, 10)
        self.assertEqual(rep.coordinates.longitude, 14)
        self.assertIsNone(rep.coordinates.elevation)
        self.assertIsNotNone(rep.modified_on)

        # shouldn't be able to change coordinates
        data = {'coordinates': {'latitude': 10, 'longitude': 15}}
        with self.assertRaises(AssertionError):
            response = self.client.patch(patch_url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # shouldn't be able to change dates
        data = {'created_on': "123"}
        response = self.client.patch(patch_url, data, format='json')

        data = {'modified_on': datetime.datetime.now()}
        response = self.client.patch(patch_url, data, format='json')

        # partial data
        data = {'coordinates': {'latitude': -10, 'longitude': -14}}
        response = self.client.post(post_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
