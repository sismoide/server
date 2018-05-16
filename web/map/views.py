from rest_framework import viewsets, mixins

from map.models import Quadrant
from map.serializers import QuadrantSerializer


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
        queryset = (top_left_corner_quads | top_right_corner_quads |
                    bot_left_corner_quads | bot_right_corner_quads).distinct()
        return queryset
