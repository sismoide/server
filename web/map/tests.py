from unittest import TestCase

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from map.models import Coordinates, Quadrant, ReportQuadrantAggregationSlice, LandmarkType, Landmark
from map.serializers import CoordinatesSerializer, QuadrantSerializer
from mobile_res.models import Report
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


def res_contain_quads(response, quad_list):
    serialized_data = QuadrantSerializer(data=response.data, many=True)
    serialized_data.is_valid()
    flag_arr = []
    for quad in quad_list:
        for res_quad in serialized_data.validated_data:
            if res_quad['min_coordinates']['latitude'] == quad.min_coordinates.latitude and \
                    res_quad['min_coordinates']['longitude'] == quad.min_coordinates.longitude and \
                    res_quad['max_coordinates']['latitude'] == quad.max_coordinates.latitude and \
                    res_quad['max_coordinates']['longitude'] == quad.max_coordinates.longitude:
                flag_arr.append(True)
                break
    return len(flag_arr) == len(quad_list)


class QuadrantsTestCase(APITestCase):
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
        """   
        Generated quads: 
            Count: 9
        
        ------------------------------------(3,3)
        |          |           |           |
        |     6    |     7     |     8     |
        -----------------------------------|(3,2)
        |          |           |           |
        |     3    |     4     |     5     |
        -----------------------------------|(3,1)
        |          |           |           |
        |     0    |     1     |     2     |
        -----------------------------------|(3,0)
        (0,0)     (1,0)        (2,0)       

        """

    def test_api_get_rcs(self):
        """
        Test api resource to get quadrants by specificing boundaries.
        :return:
        """

        def get_param_data(min_coords, max_coords):
            """
            extract parameters from Coordinates instances
            :param min_coords:
            :param max_coords:
            :return:
            """
            return {
                'min_lat': min_coords.latitude,
                'min_long': min_coords.longitude,
                'max_lat': max_coords.latitude,
                'max_long': max_coords.longitude
            }

        url = reverse('{}:quadrant-list'.format(MAP_PATH_PREFIX))

        # should return 1 quad
        min_coord_limit = Coordinates.objects.create(longitude=1, latitude=1)
        max_coord_limit = Coordinates.objects.create(longitude=2, latitude=2)

        response = self.client.get(url, get_param_data(min_coord_limit, max_coord_limit),
                                   HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertTrue(res_contain_quads(response, [self.q4, ]))

        # should return 1 quad
        min_coord_limit = Coordinates.objects.create(longitude=1.1, latitude=2.1)
        max_coord_limit = Coordinates.objects.create(longitude=1.9, latitude=2.9)

        response = self.client.get(url, get_param_data(min_coord_limit, max_coord_limit),
                                   HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertTrue(res_contain_quads(response, [self.q7, ]))

        # should return 4 quad
        min_coord_limit = Coordinates.objects.create(longitude=1, latitude=0)
        max_coord_limit = Coordinates.objects.create(longitude=3, latitude=2)

        response = self.client.get(url, get_param_data(min_coord_limit, max_coord_limit), format='json',
                                   HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 4)
        self.assertTrue(res_contain_quads(response, [self.q1, self.q2, self.q4, self.q5, ]))

        # should return 4 too
        min_coord_limit = Coordinates.objects.create(longitude=1.1, latitude=1.1)
        max_coord_limit = Coordinates.objects.create(longitude=2.9, latitude=2.9)

        response = self.client.get(url, get_param_data(min_coord_limit, max_coord_limit), format='json',
                                   HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 4)
        self.assertTrue(res_contain_quads(response, [self.q4, self.q5, self.q7, self.q8]))

        # should return 6 quad
        min_coord_limit = Coordinates.objects.create(longitude=0, latitude=0)
        max_coord_limit = Coordinates.objects.create(longitude=3, latitude=2)

        response = self.client.get(url, get_param_data(min_coord_limit, max_coord_limit), format='json',
                                   HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 6)
        self.assertTrue(res_contain_quads(response, [self.q0, self.q1, self.q2, self.q3, self.q4, self.q5, ]))

        # should return 6 quad too
        min_coord_limit = Coordinates.objects.create(longitude=0.1, latitude=0.1)
        max_coord_limit = Coordinates.objects.create(longitude=2.1, latitude=1.1)

        response = self.client.get(url, get_param_data(min_coord_limit, max_coord_limit), format='json',
                                   HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 6)
        self.assertTrue(res_contain_quads(response, [self.q0, self.q1, self.q2, self.q3, self.q4, self.q5, ]))

    def test_find_by_report_coord(self):
        r = Report.objects.create(coordinates=Coordinates.objects.create(
            latitude=1.1,
            longitude=1.1))
        self.assertEqual(self.q4, Quadrant.objects.find_by_report_coord(r))

        r = Report.objects.create(coordinates=Coordinates.objects.create(
            latitude=0.1,
            longitude=0.1))
        self.assertEqual(self.q0, Quadrant.objects.find_by_report_coord(r))

        r = Report.objects.create(coordinates=Coordinates.objects.create(
            latitude=0,
            longitude=0))
        self.assertEqual(self.q0, Quadrant.objects.find_by_report_coord(r))

        r = Report.objects.create(coordinates=Coordinates.objects.create(
            latitude=1,
            longitude=1))
        self.assertEqual(self.q4, Quadrant.objects.find_by_report_coord(r))
        self.assertNotEqual(self.q0, Quadrant.objects.find_by_report_coord(r))

        r = Report.objects.create(coordinates=Coordinates.objects.create(
            latitude=0.5,
            longitude=1))
        self.assertEqual(self.q1, Quadrant.objects.find_by_report_coord(r))
        self.assertNotEqual(self.q2, Quadrant.objects.find_by_report_coord(r))

    def test_report_quad_slice_aggregation(self):
        """
        Se agregan 2 Reports a Quadrant 0 y 4, respectivamente. 1 Report a Quadrant 1.
        :return:
        """
        self.assertEqual(0, ReportQuadrantAggregationSlice.objects.all().count())

        q0_r0 = Report.objects.create(coordinates=Coordinates.objects.create(
            latitude=0.1,
            longitude=0.1))
        q0_r1 = Report.objects.create(coordinates=Coordinates.objects.create(
            latitude=0,
            longitude=0))
        q1_r0 = Report.objects.create(coordinates=Coordinates.objects.create(
            latitude=0.5,
            longitude=1, ))
        q4_r0 = Report.objects.create(coordinates=Coordinates.objects.create(
            latitude=1.1,
            longitude=1.1),
            intensity=6)
        q4_r1 = Report.objects.create(coordinates=Coordinates.objects.create(
            latitude=1,
            longitude=1))

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

        self.assertEqual(slice_q0.report_w_intensity_count, 0)
        self.assertEqual(slice_q1.report_w_intensity_count, 0)
        self.assertEqual(slice_q4.report_w_intensity_count, 1)

        self.assertEqual(slice_q0.intensity_sum, 0)
        self.assertEqual(slice_q1.intensity_sum, 0)
        self.assertEqual(slice_q4.intensity_sum, 6)

        # update intensity of some reports
        patch_url = reverse('mobile_res:report-detail', kwargs={'pk': q0_r0.id})
        data = {'intensity': 4}
        response = self.client.patch(patch_url, data, format='json',
                                     HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        q0_r0.refresh_from_db()
        slice_q0.refresh_from_db()
        self.assertEqual(4, q0_r0.intensity)
        self.assertEqual(slice_q0.report_total_count, 2)
        self.assertEqual(slice_q0.report_w_intensity_count, 1)
        self.assertEqual(slice_q0.intensity_sum, 4)

        # try to change intensity again
        data = {'intensity': 7}
        response = self.client.patch(patch_url, data, format='json',
                                     HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        q0_r0.refresh_from_db()
        slice_q0.refresh_from_db()
        self.assertEqual(4, q0_r0.intensity)
        self.assertEqual(slice_q0.report_total_count, 2)
        self.assertEqual(slice_q0.report_w_intensity_count, 1)
        self.assertEqual(slice_q0.intensity_sum, 4)

        # update intensity of other report
        patch_url = reverse('mobile_res:report-detail', kwargs={'pk': q0_r1.id})
        data = {'intensity': 7}
        response = self.client.patch(patch_url, data, format='json',
                                     HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        q0_r1.refresh_from_db()
        slice_q0.refresh_from_db()
        self.assertEqual(7, q0_r1.intensity)
        self.assertEqual(slice_q0.report_total_count, 2)
        self.assertEqual(slice_q0.report_w_intensity_count, 2)
        self.assertEqual(slice_q0.intensity_sum, 11)

        # try to change intensity of initially full report
        patch_url = reverse('mobile_res:report-detail', kwargs={'pk': q4_r0.id})
        data = {'intensity': 4}
        response = self.client.patch(patch_url, data, format='json',
                                     HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        q4_r0.refresh_from_db()
        slice_q4.refresh_from_db()
        self.assertEqual(6, q4_r0.intensity)
        self.assertEqual(slice_q4.report_total_count, 2)
        self.assertEqual(slice_q4.report_w_intensity_count, 1)
        self.assertEqual(slice_q4.intensity_sum, 6)

        get_url = reverse('{}:get_quadrant_report_aggregation'.format(MAP_PATH_PREFIX))
        start_timestamp = timezone.now() - timezone.timedelta(minutes=15)
        end_timestamp = timezone.now() + timezone.timedelta(minutes=15)
        response = self.client.get(get_url, {
            'min_lat': -999,
            'min_long': -999,
            'max_lat': 999,
            'max_long': 999,
            'start_timestamp': start_timestamp.isoformat(),
            'end_timestamp': end_timestamp.isoformat()
        },
                                   HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)


class LandmarksTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.token = WebUser.objects.create_web_user('test_user').token
        cls.create_landmarks(cls)

    def create_landmarks(self):
        self.l_t1 = LandmarkType.objects.create(name="test_landmark_type_1")
        self.l_t2 = LandmarkType.objects.create(name="test_landmark_type_2")
        self.l0 = Landmark.objects.create(
            name="test_landmark_0",
            address="test_address_0",
            coordinates=Coordinates.objects.create(
                latitude=-1,
                longitude=-1
            ),
            type=self.l_t1
        )
        self.l1 = Landmark.objects.create(
            name="test_landmark_1",
            address="test_address_1",
            coordinates=Coordinates.objects.create(
                latitude=1,
                longitude=1
            ),
            type=self.l_t2
        )
        self.l2 = Landmark.objects.create(
            name="test_landmark_2",
            address="test_address_2",
            coordinates=Coordinates.objects.create(
                latitude=2,
                longitude=2
            ),
            type=self.l_t1
        )
        self.l3 = Landmark.objects.create(
            name="test_landmark_3",
            address="test_address_3",
            coordinates=Coordinates.objects.create(
                latitude=3,
                longitude=3
            ),
            type=self.l_t2
        )

    def test_retrieve_landmarks_by_coordinate(self):
        url = reverse('map:landmark-list')
        data = {
            'min_lat': 0,
            'min_long': 0,
            'max_lat': 1,
            'max_long': 1
        }
        response = self.client.get(url, data,
                                   HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data))
        self.assertEqual(self.l1.name, response.data[0]['name'])
        self.assertEqual(self.l1.address, response.data[0]['address'])
        self.assertAlmostEqual(self.l1.coordinates.latitude, float(response.data[0]['coordinates']['latitude']))
        self.assertAlmostEqual(self.l1.coordinates.longitude, float(response.data[0]['coordinates']['longitude']))
        self.assertEqual(self.l1.type.name, response.data[0]['type'])

        data = {
            'min_lat': 1,
            'min_long': 1,
            'max_lat': 2,
            'max_long': 2
        }
        response = self.client.get(url, data,
                                   HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data))
        data = {
            'min_lat': -1,
            'min_long': -1,
            'max_lat': 2,
            'max_long': 2
        }
        response = self.client.get(url, data,
                                   HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(3, len(response.data))

        data = {
            'min_lat': -1,
            'min_long': -1,
            'max_lat': 3,
            'max_long': 3
        }
        response = self.client.get(url, data,
                                   HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(4, len(response.data))

    def test_retrieve_landmarks_by_landmarktype_coord(self):
        url = reverse('map:landmark_type-list')
        response = self.client.get(url,
                                   HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        landmarks = response.data

        self.assertEqual(2, len(landmarks))

        url = reverse('map:landmark-list')
        data = {
            'type': landmarks[0]['name']
        }
        response = self.client.get(url, data,
                                   HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(0, len(response.data))
        data = {
            'type': landmarks[0]['name'],
            'min_lat': -9999,
            'min_long': -9999,
            'max_lat': 9999,
            'max_long': 9999
        }
        response = self.client.get(url, data,
                                   HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data))

        data = {
            'type': landmarks[1]['name'],
            'min_lat': -9999,
            'min_long': -9999,
            'max_lat': 9999,
            'max_long': 9999
        }
        response = self.client.get(url, data,
                                   HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data))

        data = {
            'type': self.l_t1,
            'min_lat': -1,
            'min_long': -1,
            'max_lat': 0,
            'max_long': 0
        }
        response = self.client.get(url, data,
                                   HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data))
        self.assertEqual(self.l0.name, response.data[0]['name'])
