from rest_framework import viewsets, mixins, status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from mobile_res.models import Report, EmergencyReport, ThreatReport, Nonce, MobileUser
from mobile_res.serializers import ReportCreateSerializer, EmergencyReportSerializer, ThreatReportSerializer, \
    ReportPatchSerializer
from web.settings import HASH_CLASS
from web_res.serializers import NonceSerializer, ChallengeSerializer


class ReportViewSet(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):

    queryset = Report.objects.all()
    serializer_class = ReportCreateSerializer
    throttle_scope = 'reports'

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
    throttle_scope = 'events'


class ThreatReportViewSet(mixins.CreateModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):
    queryset = ThreatReport.objects.all()
    serializer_class = ThreatReportSerializer
    throttle_scope = 'events'


class NonceViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Nonce.objects.all()
    serializer_class = NonceSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        nonce = Nonce.objects.create()
        ser = self.serializer_class(nonce)
        return Response(ser.data, status=status.HTTP_201_CREATED)


class ValidateChallengeAPIView(GenericAPIView):
    serializer_class = ChallengeSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return

    def post(self, request, *args, **kwargs):
        try:
            nonce_key = request.META['HTTP_AUTHORIZATION']
        except KeyError:
            return Response({}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({'invalid scheme'}, status=status.HTTP_400_BAD_REQUEST)
        validated_data = serializer.validated_data
        response_hash = validated_data['h']

        try:
            nonce = Nonce.objects.get(key=nonce_key)
            # is possible that the nonce could be expired right here in time
            # timeout_limit_time = timezone.now() - datetime.timedelta(seconds=NONCE_EXPIRATION_TIME)
            # compare
            image = HASH_CLASS(nonce.key.encode('utf-8')).hexdigest()
            if image == response_hash:
                # delete Nonce
                nonce.delete()

                # create account and return token
                mobile_user = MobileUser.objects.create_random_mobile_user()
                # Success
                return Response({'token': str(mobile_user.token)})
            else:
                # Nonce correct; hash incorrect
                return Response({}, status=403)
        except Nonce.DoesNotExist:
            # Nonce incorrect or expired
            return Response({}, status=403)
