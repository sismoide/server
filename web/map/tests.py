from unittest import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from map.models import Coordinates, Quadrant
from map.serializers import CoordinatesSerializer, QuadrantSerializer
from web.settings import MAP_PATH_PREFIX
from web_res.models import WebUser


class CoordinateOperationTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.c1 = Coordinates.objects.create(latitude=10, longitude=20)
        cls.c1_dup = Coordinates.objects.create(latitude=10, longitude=20)
        cls.c2 = Coordinates.objects.create(latitude=20, longitude=10)
        cls.center = Coordinates.objects.create(longitude=-75, latitude=-25)
        cls.left_up = Coordinates.objects.create(longitude=-77, latitude=-24)
        cls.right_up = Coordinates.objects.create(longitude=-30, latitude=-20)
        cls.left_down = Coordinates.objects.create(longitude=-77, latitude=-30)
        cls.right_down = Coordinates.objects.create(longitude=-60, latitude=-30)

    def test_equal(self):
        self.assertEqual(self.c1, self.c1_dup)
        self.assertNotEqual(self.c1, self.c2)
        self.assertNotEqual(self.c1_dup, self.c2)

    def test_order(self):
        self.assertLess(self.left_up, self.center)
        self.assertLess(self.left_down, self.center)
        self.assertLess(self.right_down, self.center)
        self.assertGreater(self.right_up, self.center)

        self.assertLessEqual(self.left_up, self.center)
        self.assertLessEqual(self.left_down, self.center)
        self.assertLessEqual(self.right_down, self.center)
        self.assertGreaterEqual(self.right_up, self.center)


class GetQuadrantsTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.token = WebUser.objects.create_web_user('test_user').token
        cls.coord_ser = CoordinatesSerializer
        cls.quad_ser = QuadrantSerializer

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

        cls.q3 = Quadrant.objects.create(
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
        cls.q4 = Quadrant.objects.create(
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
        cls.q5 = Quadrant.objects.create(
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

    def test_api_rcs(self):
        url = reverse('{}:quadrant-list'.format(MAP_PATH_PREFIX))

        min_coord_limit = Coordinates.objects.create(longitude=2, latitude=1)
        max_coord_limit = Coordinates.objects.create(longitude=3, latitude=2)

        def get_data(min_coords, max_coords):
            return {
                'min_lat': min_coords.latitude,
                'min_long': min_coords.longitude,
                'max_lat': max_coords.latitude,
                'max_long': max_coords.longitude
            }

        response = self.client.get(url, get_data(min_coord_limit, max_coord_limit),
                                   HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        min_coord_limit = Coordinates.objects.create(longitude=0, latitude=0)
        max_coord_limit = Coordinates.objects.create(longitude=3, latitude=2)

        response = self.client.get(url, get_data(min_coord_limit, max_coord_limit), format='json',
                                   HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 6)
