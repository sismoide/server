from bokeh.models import Quad
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response

from map.models import Quadrant
from map.serializers import LocationRadiusSerializer, QuadrantSerializer


class QuadrantsViewSet(mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    serializer_class = LocationRadiusSerializer
    queryset = Quadrant.objects.all()

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({'invalid scheme'}, status=status.HTTP_400_BAD_REQUEST)
        validated_data = serializer.validated_data

        min_lat = validated_data['min_coordinates']['latitude']
        min_long = validated_data['min_coordinates']['longitude']

        max_lat = validated_data['max_coordinates']['latitude']
        max_long = validated_data['max_coordinates']['longitude']

        quads = self.queryset.filter(
            min_coordinates__latitude__gte=min_lat,
            min_coordinates__longitude__gte=min_long,
            max_coordinates__latitude__lte=max_lat,
            max_coordinates__longitude__lte=max_long
        )
        print(quads.count())
        return Response(QuadrantSerializer(quads).data)

