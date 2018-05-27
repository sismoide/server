from rest_framework import viewsets, mixins
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from map.models import Quadrant
from map.serializers import QuadrantSerializer, DummySerializeR


class GetQuadrantReportAggregation(GenericAPIView):
    serializer_class = DummySerializeR

    def get_queryset(self):
        return

    def post(self, request, **kwargs):
        print(kwargs)
        ser = self.serializer_class(data=request.data)
        ser.is_valid()
        print(ser.validated_data)
        return Response(request.data)


class QuadrantReportaggregation(GenericAPIView):
    # serializer_class = ReportQuadrantAggregationSliceSerializer
    # queryset = ReportQuadrantAggregationSlice

    def get_queryset(self):
        min_lat = self.request.query_params.get('min_lat', None)
        min_long = self.request.query_params.get('min_long', None)
        max_lat = self.request.query_params.get('max_lat', None)
        max_long = self.request.query_params.get('max_long', None)
        start_timestamp = self.request.query_params('start_timestamp', None)
        end_timestamp = self.request.query_params('end_timestamp', None)

        if min_lat is None or min_long is None or max_lat is None or max_long is None:
            return Quadrant.objects.none()
        return self.queryset


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
