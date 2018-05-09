from rest_framework import viewsets, mixins

from map.models import Quadrant


class QuadrantsViewSet(mixins.ListModelMixin,
                       viewsets.GenericViewSet):

    def get_queryset(self):
        queryset = Quadrant.objects.all()
        min_lat = self.request.query_params.get('min_lat', None)
        min_long = self.request.query_params.get('min_long', None)
        max_lat = self.request.query_params.get('max_lat', None)
        max_long = self.request.query_params.get('max_long', None)

        if min_lat is None or min_long is None or max_lat is None or max_long is None:
            return Quadrant.objects.none()

        return queryset.filter(
            min_coordinates__latitude__gte=min_lat,
            min_coordinates__longitude__gte=min_long,
            max_coordinates__latitude__lte=max_lat,
            max_coordinates__longitude__lte=max_long
        )
