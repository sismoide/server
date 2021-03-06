from unittest import skip

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db import transaction
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from map.models import Quadrant, ReportQuadrantAggregationSlice
from mobile_res.models import Coordinates, Report, EmergencyType, ThreatType, ThreatReport, \
    EmergencyReport, Quake, MobileUser
from mobile_res.utils import random_username
from web.settings import HASH_CLASS, MOBILE_USER_POINTS_REPORT_SUBMIT, MOBILE_USER_POINTS_INTENSITY_UPDATE


class ModelsTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # fully defined coords
        cls.full_coord1 = Coordinates.objects.create(
            latitude=-179.555555,
            longitude=-122.123456)
        cls.full_coord2 = Coordinates.objects.create(
            latitude=179.555555,
            longitude=122.123456
        )
        cls.full_coord3 = Coordinates.objects.create(
            latitude=-179.555555,
            longitude=122.123456)
        cls.full_coord4 = Coordinates.objects.create(
            latitude=-2,
            longitude=5
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

        # long
        self.assertLess(self.full_coord1.longitude, 0)
        self.assertGreater(self.full_coord2.longitude, 0)
        self.assertGreater(self.full_coord3.longitude, 0)
        self.assertGreater(self.full_coord4.longitude, 0)

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

        # test timestamps
        old_date = timezone.datetime(1990, 3, 2, hour=16, minute=20)
        rep = Report.objects.create(coordinates=self.full_coord1, created_on=old_date)
        self.assertEqual(old_date, rep.created_on)
        self.assertLess(old_date.year, rep.modified_on.year
                        )

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
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.m_user = MobileUser.objects.create_random_mobile_user()
        cls.token = cls.m_user.token
        cls.token2 = MobileUser.objects.create_random_mobile_user().token

    def test_partial_report(self):
        """
        Ensure that can create and patch a report
        :return:
        """

        post_url = reverse('mobile_res:report-list')

        # partial data
        data = {'coordinates': {'latitude': 10, 'longitude': 14}}
        # test post without key
        response = self.client.post(post_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(post_url, data, format='json', HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Report.objects.count(), 1)

        # test data integrity
        rep = Report.objects.all()[0]
        self.assertIsNone(rep.intensity)
        self.assertIsNotNone(rep.created_on)
        self.assertIsNotNone(rep.modified_on)
        #        self.assertEqual(rep.created_on.minute, rep.modified_on.minute)
        past_modified_on = rep.modified_on
        past_created_on = rep.created_on

        self.assertIsNotNone(rep.coordinates)
        self.assertEqual(rep.coordinates.latitude, 10)
        self.assertEqual(rep.coordinates.longitude, 14)
        #        self.assertEqual(rep.created_on.second, rep.modified_on.second)
        self.assertIsNotNone(rep.modified_on)
        self.assertNotEqual(rep.created_on, rep.modified_on)

        # suppose now i have the intensity
        report_id = response.data['id']
        patch_url = reverse('mobile_res:report-detail', kwargs={'pk': report_id})
        data = {'intensity': 4}
        # try without token
        response = self.client.patch(patch_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # with token
        response = self.client.patch(patch_url, data, format='json',
                                     HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Report.objects.count(), 1)
        self.assertEqual(
            data['intensity'],
            Report.objects.get(id=report_id).intensity
        )

        # try to change intensity again
        data = {'intensity': 7}
        response = self.client.patch(patch_url, data, format='json',
                                     HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(data['intensity'], Report.objects.get(id=report_id).intensity)
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
        self.assertIsNotNone(rep.modified_on)

        # shouldn't be able to change coordinates
        data = {'coordinates': {'latitude': 66, 'longitude': 77}}
        # with self.assertRaises(AssertionError):
        response = self.client.patch(patch_url, data, format='json',
                                     HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(
            data['coordinates']['latitude'],
            Report.objects.get(id=report_id).coordinates.latitude
        )
        self.assertNotEqual(
            data['coordinates']['longitude'],
            Report.objects.get(id=report_id).coordinates.longitude
        )

        # shouldn't be able to change dates
        new_time = timezone.now()
        data = {'created_on': new_time}
        response = self.client.patch(patch_url, data, format='json',
                                     HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(new_time, Report.objects.get(id=report_id).created_on)

        new_time = timezone.now()
        data = {'modified_on': new_time}
        response = self.client.patch(patch_url, data, format='json',
                                     HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(new_time, Report.objects.get(id=report_id).modified_on)

        new_time = timezone.now()
        data = {'created_on': new_time, 'modified_on': new_time}
        response = self.client.patch(patch_url, data, format='json',
                                     HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertNotEqual(new_time, Report.objects.get(id=report_id).modified_on)
        self.assertNotEqual(new_time, Report.objects.get(id=report_id).created_on)

        # partial data
        data = {'coordinates': {'latitude': -10, 'longitude': -14}}
        response = self.client.post(post_url, data, format='json', HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_nonce_challenge(self):
        create_nonce_url = reverse("mobile_res:nonce-list")
        challenge_url = reverse("mobile_res:challenge")

        res = self.client.post(create_nonce_url)
        self.assertEqual(status.HTTP_201_CREATED, res.status_code)
        nonce = res.data['key']
        challenge_response = HASH_CLASS(nonce.encode('utf-8')).hexdigest()
        # correct challenge_response, no nonce case should error
        res = self.client.post(challenge_url, {'h': challenge_response})
        self.assertEqual(status.HTTP_403_FORBIDDEN, res.status_code)

        # incorrect challenge_response, correct nonce should error
        res = self.client.post(create_nonce_url)
        self.assertEqual(status.HTTP_201_CREATED, res.status_code)
        second_nonce = res.data['key']
        res = self.client.post(challenge_url,
                               {'h': HASH_CLASS(second_nonce.encode('utf-8')).hexdigest()},
                               HTTP_AUTHORIZATION=nonce)
        self.assertEqual(status.HTTP_403_FORBIDDEN, res.status_code)

        # empty challenge_response, correct nonce should error
        res = self.client.post(challenge_url, {'h': ""}, HTTP_AUTHORIZATION=nonce)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, res.status_code)

        # correct challenge_response, correct nonce should pass and return token
        res = self.client.post(challenge_url, {'h': challenge_response}, HTTP_AUTHORIZATION=nonce)
        self.assertEqual(status.HTTP_200_OK, res.status_code)
        self.assertIsInstance(res.data['token'], type(""))

        # now check that nonce can't be used again
        res = self.client.post(challenge_url, {'h': challenge_response}, HTTP_AUTHORIZATION=nonce)
        self.assertEqual(status.HTTP_403_FORBIDDEN, res.status_code)

    def test_report_creator_assoc(self):
        post_url = reverse('mobile_res:report-list')

        # post report as user 1
        data = {'coordinates': {'latitude': 10, 'longitude': 14}}
        response = self.client.post(
            post_url,
            data,
            format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        report_1_id = response.data['id']

        r = Report.objects.get(pk=report_1_id)
        self.assertEqual(self.m_user.user, r.creator)


    def test_report_patch(self):
        post_url = reverse('mobile_res:report-list')

        # post report as user 1
        data = {'coordinates': {'latitude': 10, 'longitude': 14}}
        response = self.client.post(
            post_url,
            data,
            format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        report_1_id = response.data['id']
        r = Report.objects.get(pk=report_1_id)
        self.assertEqual(self.m_user.user, r.creator)

        # post report as user 2
        data = {'coordinates': {'latitude': 11, 'longitude': 15}}
        response = self.client.post(
            post_url,
            data,
            format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token2.key)
        )
        report_2_id = response.data['id']

        # post report as internal call
        report_3_id = Report.objects.create(
            coordinates=Coordinates.objects.create(
                longitude=16,
                latitude=12)
        ).id

        # try to patch
        data = {'intensity': 4}
        patch_1_url = reverse('mobile_res:report-detail',
                              kwargs={'pk': report_1_id})
        patch_2_url = reverse('mobile_res:report-detail',
                              kwargs={'pk': report_2_id})
        patch_3_url = reverse('mobile_res:report-detail',
                              kwargs={'pk': report_3_id})

        # User 1 cases
        # try to patch other user's report should fail
        response = self.client.patch(
            patch_2_url,
            data,
            format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # try to patch anon report's should pass
        response = self.client.patch(
            patch_3_url,
            data,
            format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # user 2 cases
        # try to patch user 1's report should fail
        response = self.client.patch(
            patch_1_url,
            data,
            format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token2.key))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # try to patch it's own report should pass
        response = self.client.patch(
            patch_2_url,
            data,
            format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token2.key))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # try to patch anon report already patched should fail
        response = self.client.patch(
            patch_3_url,
            data,
            format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # user 1 more cases
        # try to patch user 2's report again (after user 1 patched), should error
        response = self.client.patch(
            patch_2_url,
            data,
            format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # try to patch his own report, should pass
        response = self.client.patch(
            patch_1_url,
            data,
            format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UtilTestCase(TestCase):
    def test_random_username(self):
        """
        Check uniqueness of *iter_limit* random user-names generated
        :return:
        """
        iter_limit = 100000
        username_list = []
        for i in range(iter_limit):
            username_list.append(random_username())

        username_set = set(username_list)
        self.assertEqual(len(username_set), len(username_list))


class NearbyReportsTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.token = MobileUser.objects.create_random_mobile_user().token

        cls.coord1 = Coordinates.objects.create(
            latitude=50.0,
            longitude=50.0
        )
        cls.coord2 = Coordinates.objects.create(
            latitude=51.0,
            longitude=50.0
        )
        cls.coord3 = Coordinates.objects.create(
            latitude=60.0,
            longitude=50.0
        )
        cls.coord4 = Coordinates.objects.create(
            latitude=50.0,
            longitude=51.0
        )
        cls.coord5 = Coordinates.objects.create(
            latitude=50.0,
            longitude=60.0
        )

        cls.lim_coord1 = Coordinates.objects.create(
            latitude=80.0,
            longitude=179.0
        )

        cls.rep1 = Report.objects.create(
            coordinates=cls.coord1,
            intensity=4
        )
        cls.rep2 = Report.objects.create(
            coordinates=cls.coord2,
            intensity=5
        )
        cls.rep3 = Report.objects.create(
            coordinates=cls.coord3,
            intensity=6
        )
        cls.rep4 = Report.objects.create(
            coordinates=cls.coord4,
            intensity=7
        )
        cls.rep5 = Report.objects.create(
            coordinates=cls.coord5,
            intensity=8
        )
        cls.rep6 = Report.objects.create(
            coordinates=cls.coord2,
            intensity=7,
            created_on=timezone.now()-timezone.timedelta(hours=1)
        )
        cls.rep7 = Report.objects.create(
            coordinates=cls.coord2,
            intensity=5,
            created_on=timezone.now()-timezone.timedelta(days=1000)
        )

        cls.lim_rep1 = Report.objects.create(
            coordinates=cls.lim_coord1,
            intensity=9
        )

    def test_regular_coords(self):
        url = reverse('mobile_res:nearby-reports-list')
        data = {'latitude': '50.0', 'longitude': '50.0', 'rad': '200'}
        response = self.client.get(url, data, HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)

    def test_date_filter(self):
        url = reverse('mobile_res:nearby-reports-list')
        data = {'latitude': '50.0',
                'longitude': '50.0',
                'rad': '200',
                'start': (timezone.now()-timezone.timedelta(days=15)).strftime("%Y-%m-%dT%H:%M"),
                'end': timezone.now().strftime("%Y-%m-%dT%H:%M")}
        response = self.client.get(url, data, HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)


    @skip
    def test_limit_coords(self):
        url = reverse('mobile_res:nearby-reports-list')
        data = {'latitude': '80', 'longitude': '-179', 'rad': '200'}
        response = self.client.get(url, data, HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_invalid_request(self):
        url = reverse('mobile_res:nearby-reports-list')
        data = {'latitude': 'hola', 'longitude': '-179', 'rad': '200'}
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(url, data, HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {'latitude': '80', 'longitude': 'HOLA', 'rad': '200'}
        response = self.client.get(url, data, HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {'latitude': '80', 'longitude': '-179', 'rad': 'chao'}
        response = self.client.get(url, data, HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class QuakeModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.coord1 = Coordinates.objects.create(
            latitude=-33.45,
            longitude=-70.66
        )

        cls.coord2 = Coordinates.objects.create(
            latitude=-35.5,
            longitude=-71
        )

        cls.quake1 = Quake.objects.create(
            eventid='quake1',
            coordinates=cls.coord1,
            depth=20,
            magnitude=7.7,
            timestamp=timezone.datetime(2018, 5, 1, hour=12)
        )

        cls.quake2 = Quake.objects.create(
            eventid='quake2',
            coordinates=cls.coord2,
            depth=5.5,
            magnitude=9.3,
            timestamp=timezone.datetime(2018, 4, 24, hour=18, minute=30)
        )

    def test_quakes(self):
        self.assertIsNotNone(self.quake1)
        self.assertIsNotNone(self.quake2)

        with self.assertRaises(ValidationError):
            Quake.objects.create(
                coordinates=self.coord1,
                depth=-5,
                magnitude=5.4,
                timestamp=timezone.datetime(2017, 1, 1, hour=1, minute=1)
            )
            Quake.objects.create(
                coordinates=self.coord2,
                depth=35,
                magnitude=-7.1,
                timestamp=timezone.datetime(2012, 12, 12, hour=12, minute=12)
            )


class NearbyQuakeTests(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.token = MobileUser.objects.create_random_mobile_user().token

        cls.coord1 = Coordinates.objects.create(
            latitude=-33.45,
            longitude=-70.66
        )

        cls.coord2 = Coordinates.objects.create(
            latitude=-35.5,
            longitude=-71
        )

        cls.coord3 = Coordinates.objects.create(
            latitude=-40.3,
            longitude=-70.5
        )

        cls.quake1 = Quake.objects.create(
            eventid='quake1,',
            coordinates=cls.coord1,
            depth=20,
            magnitude=7.7,
            timestamp=timezone.datetime(2017, 5, 1, hour=12)
        )

        cls.quake2 = Quake.objects.create(
            eventid='quake2',
            coordinates=cls.coord2,
            depth=5.5,
            magnitude=9.3,
            timestamp=timezone.datetime(2018, 4, 24, hour=18, minute=30)
        )

        cls.quake3 = Quake.objects.create(
            eventid='quake3',
            coordinates=cls.coord1,
            depth=50.4,
            magnitude=6.7,
            timestamp=timezone.now() - timezone.timedelta(minutes=30)
        )

        cls.quake4 = Quake.objects.create(
            eventid='quake4',
            coordinates=cls.coord3,
            depth=40.6,
            magnitude=6.3,
            timestamp=timezone.now() - timezone.timedelta(minutes=5)
        )

    def test_get_all_quakes(self):
        url = reverse('mobile_res:quake-list')
        response = self.client.get(url, HTTP_AUTHORIZATION="Token {}".format(self.token.key))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_get_relevant_quakes(self):
        url = reverse('mobile_res:nearby-quakes-list')
        data = {'latitude': '-33.45', 'longitude': '-70.66',
                'start': (timezone.now() - timezone.timedelta(days=90)).strftime("%Y-%m-%dT%H:%M"),
                'end': timezone.now().strftime("%Y-%m-%dT%H:%M")}

        response = self.client.get(url, data, HTTP_AUTHORIZATION="Token {}".format(self.token.key))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        data = {'latitude': 'hola', 'longitude': '-70.66',
                'start': (timezone.now() - timezone.timedelta(days=90)).strftime("%Y-%m-%dT%H:%M"),
                'end': timezone.now().strftime("%Y-%m-%dT%H:%M")}

        response = self.client.get(url, data, HTTP_AUTHORIZATION="Token {}".format(self.token.key))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {'latitude': '-33.45', 'longitude': 'HOLA',
                'start': (timezone.now() - timezone.timedelta(days=90)).strftime("%Y-%m-%dT%H:%M"),
                'end': timezone.now().strftime("%Y-%m-%dT%H:%M")}

        response = self.client.get(url, data, HTTP_AUTHORIZATION="Token {}".format(self.token.key))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {'latitude': '-33.45', 'longitude': '-70.66'}

        response = self.client.get(url, data, HTTP_AUTHORIZATION="Token {}".format(self.token.key))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class MobileUserPointSystemTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # create mobile user
        cls.m_user = MobileUser.objects.create_random_mobile_user()
        # create quadrants
        # y = 0
        cls.q0 = Quadrant.objects.create(
            min_coordinates=Coordinates.objects.create(
                longitude=0,
                latitude=0
            ),
            max_coordinates=Coordinates.objects.create(
                longitude=1,
                latitude=1
            ),
            map_relative_pos_x=0,
            map_relative_pos_y=0
        )
        cls.q1 = Quadrant.objects.create(
            min_coordinates=Coordinates.objects.create(
                longitude=1,
                latitude=0
            ),
            max_coordinates=Coordinates.objects.create(
                longitude=2,
                latitude=1
            ),
            map_relative_pos_x=1,
            map_relative_pos_y=0)

        cls.q2 = Quadrant.objects.create(
            min_coordinates=Coordinates.objects.create(
                longitude=2,
                latitude=0
            ),
            max_coordinates=Coordinates.objects.create(
                longitude=3,
                latitude=1
            ),
            map_relative_pos_x=2,
            map_relative_pos_y=0)
        # y = 1
        cls.q3 = Quadrant.objects.create(
            min_coordinates=Coordinates.objects.create(
                longitude=0,
                latitude=1
            ),
            max_coordinates=Coordinates.objects.create(
                longitude=1,
                latitude=2
            ),
            map_relative_pos_x=0,
            map_relative_pos_y=1)
        cls.q4 = Quadrant.objects.create(
            min_coordinates=Coordinates.objects.create(
                longitude=1,
                latitude=1
            ),
            max_coordinates=Coordinates.objects.create(
                longitude=2,
                latitude=2
            ),
            map_relative_pos_x=1,
            map_relative_pos_y=1)
        cls.q5 = Quadrant.objects.create(
            min_coordinates=Coordinates.objects.create(
                longitude=2,
                latitude=1
            ),
            max_coordinates=Coordinates.objects.create(
                longitude=3,
                latitude=2
            ),
            map_relative_pos_x=2,
            map_relative_pos_y=1)
        # y = 2
        cls.q6 = Quadrant.objects.create(
            min_coordinates=Coordinates.objects.create(
                longitude=0,
                latitude=2
            ),
            max_coordinates=Coordinates.objects.create(
                longitude=1,
                latitude=3
            ),
            map_relative_pos_x=0,
            map_relative_pos_y=1)
        cls.q7 = Quadrant.objects.create(
            min_coordinates=Coordinates.objects.create(
                longitude=1,
                latitude=2
            ),
            max_coordinates=Coordinates.objects.create(
                longitude=2,
                latitude=3
            ),
            map_relative_pos_x=1,
            map_relative_pos_y=1)
        cls.q8 = Quadrant.objects.create(
            min_coordinates=Coordinates.objects.create(
                longitude=2,
                latitude=2
            ),
            max_coordinates=Coordinates.objects.create(
                longitude=3,
                latitude=3
            ),
            map_relative_pos_x=2,
            map_relative_pos_y=1)

    def test_point_addition(self):
        self.assertEqual(0, self.m_user.points)

        # partial data report
        post_url = reverse('mobile_res:report-list')
        post_data = {'coordinates': {'latitude': 10, 'longitude': 14}}
        response = self.client.post(post_url, post_data, format='json', HTTP_AUTHORIZATION="Token {}".format(
            self.m_user.token.key)
                                    )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.m_user.refresh_from_db()
        expected_points = MOBILE_USER_POINTS_REPORT_SUBMIT
        self.assertEqual(expected_points, self.m_user.points)

        # patch intensity report
        patch_data = {'intensity': 4}
        patch_url = reverse('mobile_res:report-detail',
                            kwargs={'pk': response.data['id']})
        response = self.client.patch(
            patch_url,
            patch_data,
            format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.m_user.token.key))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.m_user.refresh_from_db()
        expected_points += MOBILE_USER_POINTS_INTENSITY_UPDATE
        self.assertEqual(expected_points, self.m_user.points)

        # partial data +1 report
        post_url = reverse('mobile_res:report-list')
        post_data = {'coordinates': {'latitude': 10, 'longitude': 14}}
        response = self.client.post(post_url, post_data, format='json', HTTP_AUTHORIZATION="Token {}".format(
            self.m_user.token.key)
                                    )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.m_user.refresh_from_db()
        expected_points += MOBILE_USER_POINTS_REPORT_SUBMIT
        self.assertEqual(expected_points, self.m_user.points)

    def test_quadrant_confidence(self):
        # partial data report
        post_url = reverse('mobile_res:report-list')
        m_user = MobileUser.objects.create_random_mobile_user()

        q0_r0_data = {'coordinates': {'latitude': 0.1, 'longitude': .1}}
        q0_r1_data = {'coordinates': {'latitude': 0, 'longitude': 0}}
        q1_r0_data = {'coordinates': {'latitude': .5, 'longitude': 1}}
        q4_r0_data = {'coordinates': {'latitude': 1.1, 'longitude': 1.1}}
        q4_r1_data = {'coordinates': {'latitude': 1, 'longitude': 1}}

        response = self.client.post(post_url, q0_r0_data, format='json', HTTP_AUTHORIZATION="Token {}".format(
            m_user.token.key)
                                    )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(post_url, q0_r1_data, format='json', HTTP_AUTHORIZATION="Token {}".format(
            m_user.token.key)
                                    )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(post_url, q1_r0_data, format='json', HTTP_AUTHORIZATION="Token {}".format(
            m_user.token.key)
                                    )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(post_url, q4_r0_data, format='json', HTTP_AUTHORIZATION="Token {}".format(
            m_user.token.key)
                                    )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(post_url, q4_r1_data, format='json', HTTP_AUTHORIZATION="Token {}".format(
            m_user.token.key)
                                    )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.m_user.refresh_from_db()

        self.assertNotEqual(0, ReportQuadrantAggregationSlice.objects.all().count())
        self.assertEqual(1, ReportQuadrantAggregationSlice.objects.filter(quadrant=self.q0).count())
        self.assertEqual(1, ReportQuadrantAggregationSlice.objects.filter(quadrant=self.q1).count())
        self.assertEqual(0, ReportQuadrantAggregationSlice.objects.filter(quadrant=self.q2).count())
        self.assertEqual(0, ReportQuadrantAggregationSlice.objects.filter(quadrant=self.q3).count())
        self.assertEqual(1, ReportQuadrantAggregationSlice.objects.filter(quadrant=self.q4).count())
        self.assertEqual(0, ReportQuadrantAggregationSlice.objects.filter(quadrant=self.q5).count())

        slice_q0 = ReportQuadrantAggregationSlice.objects.get(quadrant=self.q0)
        slice_q1 = ReportQuadrantAggregationSlice.objects.get(quadrant=self.q1)
        slice_q4 = ReportQuadrantAggregationSlice.objects.get(quadrant=self.q4)

        self.assertEqual(slice_q0.report_total_count, 2)
        self.assertEqual(slice_q1.report_total_count, 1)
        self.assertEqual(slice_q4.report_total_count, 2)

        self.assertEqual(3, slice_q0.points_sum)
        self.assertEqual(3, slice_q1.points_sum)
        self.assertEqual(9, slice_q4.points_sum)
