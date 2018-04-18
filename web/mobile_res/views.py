from rest_framework import viewsets, mixins

from mobile_res.models import Report, EmergencyReport, ThreatReport
from mobile_res.serializers import ReportCreateSerializer, EmergencyReportSerializer, ThreatReportSerializer, \
    ReportPatchSerializer


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
