from rest_framework import mixins, viewsets, permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from mobile_res.models import Report, EmergencyReport, ThreatReport
from mobile_res.utils import get_start_and_end_dates
from web_res.models import WebUser
from web_res.serializers import ReportSerializer, WebUserChangePasswordSerializer, EmergencySerializer, ThreatSerializer


class ReportList(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(created_on__range=get_start_and_end_dates(request))
        serializer = ReportSerializer(queryset, many=True)
        return Response(serializer.data)


class EmergencyList(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = EmergencyReport.objects.all()
    serializer_class = EmergencySerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(report__created_on__range=get_start_and_end_dates(request))
        serializer = EmergencySerializer(queryset, many=True)
        return Response(serializer.data)


class ThreatList(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = ThreatReport.objects.all()
    serializer_class = ThreatSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(report__created_on__range=get_start_and_end_dates(request))
        serializer = ThreatSerializer(queryset, many=True)
        return Response(serializer.data)


class WebUserChangePassword(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = WebUserChangePasswordSerializer

    def get_queryset(self):
        return

    def post(self, request):
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
