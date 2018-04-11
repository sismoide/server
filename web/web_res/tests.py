from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from mobile_res.models import Report, Coordinates
import datetime as dt


# Create your tests here.

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
			username='juan',
			created_on=dt.datetime(1990, 8, 23, hour=13, minute=37)
		)
		cls.report2 = Report.objects.create(
			coordinates=cls.part_coord1,
			intensity=8,
			username='rodrigo',
			created_on=dt.datetime(2018, 10, 5, hour=12, minute=3)
		)

	def test_get_reports(self):
		url = reverse('web_res:report-list')
		data = {'start': '2018-01-01T00:00', 'end': '2018-12-31T00:00'}
		response = self.client.get(url, data)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
