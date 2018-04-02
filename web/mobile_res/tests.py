from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db import transaction
from django.db.models import ProtectedError
from django.test import TestCase

from mobile_res.models import Coordinates, Report, Question, Answer


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
                                            intensity=1, username='pepito')

        cls.report2 = Report.objects.create(coordinates=cls.parc_coord1,
                                            intensity=12, username='juan')

        cls.report3 = Report.objects.create(coordinates=cls.parc_coord3,
                                            intensity=5, username='pepito')

        # questions
        cls.q4 = Question.objects.create(text="cuarta pregunta?", position=4)
        cls.q1 = Question.objects.create(text="primera pregunta?", position=1)
        cls.q3 = Question.objects.create(text="tercera pregunta?", position=3)
        cls.q2 = Question.objects.create(text="segunda pregunta?", position=2)

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

        self.assertIsNotNone(self.report1.timestamp)
        self.assertIsNotNone(self.report2.timestamp)

        with self.assertRaises(ProtectedError):
            self.full_coord1.delete()
            self.parc_coord1.delete()

    def test_question(self):
        q0 = Question.objects.create(text='pregunta 0', position=0)
        questions = Question.objects.all()  # should be gathered in order

        self.assertEqual(questions[3], self.q3)
        self.assertEqual(questions[2], self.q2)
        self.assertEqual(questions[0], q0)
        self.assertEqual(questions[1], self.q1)
        self.assertEqual(questions[4], self.q4)

        with self.assertRaises(IntegrityError):
            # add question in same position
            Question.objects.create(text='other question 1', position=1)
            Question.objects.create(text='primera pregunta?', position=999)

    def test_answer(self):
        questions = Question.objects.all()
        for question in questions:
            # read question
            self.assertIsInstance(question.text, str)
            # answer it
            Answer.objects.create(
                text='si',
                question=question,
                report=self.report1
            )

        # try to answer again will raise error
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Answer.objects.create(
                    text='en verdad no',
                    question=questions[0],
                    report=self.report1)

        # but if answer is edited all is ok
        with transaction.atomic():
            ans = Answer.objects.get(question=questions[0], report=self.report1)
        ans.text = 'en verdad no'
        ans.save()
        self.assertEqual(ans.text, 'en verdad no')
