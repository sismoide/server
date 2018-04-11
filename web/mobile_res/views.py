from rest_framework import viewsets, mixins

from mobile_res.models import Report
from mobile_res.serializers import ReportSerializer


class ReportViewSet(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
