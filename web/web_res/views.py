import datetime as dt

from rest_framework import mixins, viewsets, permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from mobile_res.models import EmergencyReport, ThreatReport
from mobile_res.models import Report
from web_res.models import WebUser
from web_res.serializers import EmergencySerializer, ThreatSerializer
from web_res.serializers import IntensitySerializer, WebUserChangePasswordSerializer


def get_date(request, date_type, default):
    date = request.query_params.get(date_type, default)
    return dt.datetime.strptime(date, "%Y-%m-%dT%H:%M")


# obtiene las fechas del request
def getdates(request):
    start_date = get_date(request, 'start', "1918-01-01T00:00")
    end_date = get_date(request, 'end', "2100-12-31T23:59")
    return start_date, end_date


class ReportList(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Report.objects.all()
    serializer_class = IntensitySerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(created_on__range=getdates(request))
        serializer = IntensitySerializer(queryset, many=True)
        return Response(serializer.data)


class EmergencyList(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = EmergencyReport.objects.all()
    serializer_class = EmergencySerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(report__created_on__range=getdates(request))
        serializer = EmergencySerializer(queryset, many=True)
        return Response(serializer.data)


class ThreatList(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = ThreatReport.objects.all()
    serializer_class = ThreatSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(report__created_on__range=getdates(request))
        serializer = ThreatSerializer(queryset, many=True)
        return Response(serializer.data)


class WebUserChangePassword(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = WebUserChangePasswordSerializer

    def get_queryset(self):
        return

    def post(self, request, *args, **kwargs):
        django_user = request.user
        try:
            web_user = WebUser.objects.get(user=django_user)
        except WebUser.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        ser = self.serializer_class(data=request.data)
        if not ser.is_valid():
            return Response({'info': 'password should have 8+ characters'}, status=status.HTTP_400_BAD_REQUEST)
        validated_data = ser.validated_data

        web_user.user.set_password(validated_data['password'])
        web_user.user.save()  # token is changed
        return Response({'token': str(WebUser.objects.get(user=django_user).token)}, status=status.HTTP_202_ACCEPTED)
