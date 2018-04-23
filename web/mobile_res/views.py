from rest_framework import viewsets, mixins
from rest_framework.response import Response

from mobile_res.models import Report, EmergencyReport, ThreatReport
from mobile_res.serializers import ReportCreateSerializer, EmergencyReportSerializer, ThreatReportSerializer, \
    ReportPatchSerializer
from web_res.serializers import ReportSerializer

from math import cos, radians


class ReportViewSet(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):

    queryset = Report.objects.all()
    serializer_class = ReportCreateSerializer

    def get_serializer_class(self):
        serializer_class = self.serializer_class

        if self.request.method == 'PATCH':
            serializer_class = ReportPatchSerializer
        return serializer_class


class EmergencyReportViewSet(mixins.CreateModelMixin,
                             mixins.UpdateModelMixin,
                             viewsets.GenericViewSet):
    queryset = EmergencyReport.objects.all()
    serializer_class = EmergencyReportSerializer


class ThreatReportViewSet(mixins.CreateModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):
    queryset = ThreatReport.objects.all()
    serializer_class = ThreatReportSerializer


def get_limits(request):
    # in kilometers
    #radius = 200.0
    radius = float(request.query_params.get('rad', "10.0"))

    # length of 1 degree at the equator (latitude and longitude)
    km_p_deg_lat = 110.57
    km_p_deg_long = 111.32

    current_lat = float(request.query_params.get('latitude', "50.0"))
    current_long = float(request.query_params.get('longitude', "50.0"))

    min_lat = current_lat - (radius/km_p_deg_lat)
    max_lat = current_lat + (radius/km_p_deg_lat)

    # length of 1 longitude degree (varies with latitude)
    deg_length = cos(radians(current_lat)) * km_p_deg_long

    min_long = current_long - (radius/deg_length)
    max_long = current_long + (radius/deg_length)

    return min_lat, max_lat, min_long, max_long


# get nearby reports
# does NOT work close to the poles, or close to +180/-180 longitude
class NearbyReportsList(mixins.ListModelMixin,
                        viewsets.GenericViewSet):

    queryset = Report.objects.all()
    serializer_class = ReportSerializer

    def list(self, request, *args, **kwargs):
        min_lat, max_lat, min_long, max_long = get_limits(request)
        queryset = self.get_queryset().filter(coordinates__latitude__range=(min_lat, max_lat))
        queryset = queryset.filter(coordinates__longitude__range=(min_long, max_long))
        serializer = ReportSerializer(queryset, many=True)
        return Response(serializer.data)
