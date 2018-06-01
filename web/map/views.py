from django.utils.dateparse import parse_datetime
from rest_framework import viewsets, mixins, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from map.models import Quadrant, ReportQuadrantAggregationSlice
from map.serializers import QuadrantSerializer, DummySerializeR, ReportQuadrantAggregationSliceSerializer


class GetQuadrantReportAggregation(GenericAPIView):
    serializer_class = DummySerializeR

    def get_queryset(self):
        return

    def get(self, request, **kwargs):
        min_lat = self.request.query_params.get('min_lat', None)
        min_long = self.request.query_params.get('min_long', None)
        max_lat = self.request.query_params.get('max_lat', None)
        max_long = self.request.query_params.get('max_long', None)
        start_timestamp = self.request.query_params.get('start_timestamp', None)
        end_timestamp = self.request.query_params.get('end_timestamp', None)

        if min_lat is None or \
                min_long is None or \
                max_lat is None or \
                max_long is None or \
                start_timestamp is None or \
                end_timestamp is None:
            return Response({'status': "query param not specified. "
                                       "Need min_lat, min_long, max_lat, max_long, start_timestamp and end_timestamp"},
                            status=status.HTTP_400_BAD_REQUEST)

        # parse start_timestamp
        try:
            start_timestamp = parse_datetime(start_timestamp)
            if start_timestamp is None:
                return Response({'status': 'invalid start_timestamp. Should be in ISO 8601. '
                                           'Ex. \'2016-12-11T09:27:24.895\''},
                                status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'status': 'invalid start_timestamp. {}'.format(e)},
                            status=status.HTTP_400_BAD_REQUEST)

        # parse end_timestamp
        try:
            end_timestamp = parse_datetime(end_timestamp)
            if end_timestamp is None:
                return Response({'status': 'invalid end_timestamp. Should be in ISO 8601. '
                                           'Ex. \'2016-12-11T09:27:24\''},
                                status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'status': 'invalid end_timestamp. {}. Ex. \'2016-12-11T09:27:24\''.format(e)},
                            status=status.HTTP_400_BAD_REQUEST)

        # get report-quadrant-aggregation-slices submitted between this times
        queryset = ReportQuadrantAggregationSlice.objects.filter(
            start_timestamp__gte=start_timestamp,
            end_timestamp__lte=end_timestamp)

        quadrant_set = set(queryset.values_list('quadrant', flat=True))
        res = []
        for quadrant_id in quadrant_set:
            quadrant_data = QuadrantSerializer(Quadrant.objects.get(pk=quadrant_id)).data
            quadrant_data['id'] = quadrant_id

            slices_data = ReportQuadrantAggregationSliceSerializer(
                queryset.filter(quadrant=quadrant_id),
                many=True
            ).data

            res.append({'quadrant_data': quadrant_data,
                        'slices_data': slices_data})
        # todo: probar que retorne mas de un slice cuando hay reportes espaciados por 15 mins o masquad
        return Response(res, status=status.HTTP_200_OK)


class QuadrantsViewSet(mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    serializer_class = QuadrantSerializer
    queryset = Quadrant.objects.all()

    def get_queryset(self):
        min_lat = self.request.query_params.get('min_lat', None)
        min_long = self.request.query_params.get('min_long', None)
        max_lat = self.request.query_params.get('max_lat', None)
        max_long = self.request.query_params.get('max_long', None)

        if min_lat is None or min_long is None or max_lat is None or max_long is None:
            return Quadrant.objects.none()

        top_left_corner_quads = self.queryset.filter(
            min_coordinates__longitude__gte=min_long,
            min_coordinates__longitude__lt=max_long,
            max_coordinates__latitude__gt=min_lat,
            max_coordinates__latitude__lte=max_lat
        )

        top_right_corner_quads = self.queryset.filter(
            max_coordinates__longitude__gt=min_long,
            max_coordinates__longitude__lte=max_long,
            max_coordinates__latitude__gt=min_lat,
            max_coordinates__latitude__lte=max_lat
        )

        bot_left_corner_quads = self.queryset.filter(
            min_coordinates__longitude__gte=min_long,
            min_coordinates__longitude__lt=max_long,
            min_coordinates__latitude__gte=min_lat,
            min_coordinates__latitude__lt=max_lat
        )

        bot_right_corner_quads = self.queryset.filter(
            max_coordinates__longitude__gt=min_long,
            max_coordinates__longitude__lte=max_long,
            min_coordinates__latitude__gte=min_lat,
            min_coordinates__latitude__lt=max_lat
        )

        smaller_viewport_corner_case_quad = self.queryset.filter(
            max_coordinates__longitude__gt=max_long,
            max_coordinates__latitude__gt=max_lat,
            min_coordinates__longitude__lt=min_long,
            min_coordinates__latitude__lt=min_lat
        )

        queryset = (top_left_corner_quads | top_right_corner_quads |
                    bot_left_corner_quads | bot_right_corner_quads |
                    smaller_viewport_corner_case_quad).distinct()
        return queryset
