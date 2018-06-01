from math import cos, radians

from rest_framework import viewsets, mixins, status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from mobile_res.models import EmergencyReport, ThreatReport, Quake, Nonce, MobileUser, Report
from mobile_res.serializers import ReportCreateSerializer, EmergencyReportSerializer, ThreatReportSerializer, \
    ReportPatchSerializer, QuakeSerializer
from web.settings import HASH_CLASS
from web_res.serializers import NonceSerializer, ChallengeSerializer
from web_res.serializers import ReportSerializer
from web_res.views import getdates

from math import cos, radians
from web_res.serializers import NonceSerializer, ChallengeSerializer, ReportSerializer


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

    def post(self, request):
        # TODO: quitar texto de errores en status 403
        try:
            nonce_key = request.META['HTTP_AUTHORIZATION']
        except KeyError:
            return Response({'HTTP_AUTHORIZATION header not found'}, status=status.HTTP_403_FORBIDDEN)

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
                return Response({"correct nonce, incorrect hash"}, status=403)
        except Nonce.DoesNotExist:
            # Nonce incorrect or expired
            return Response({"incorrect nonce or expired"}, status=403)


def get_limits(request):
    # in kilometers
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
    throttle_scope = 'mobile-read'

    def list(self, request, *args, **kwargs):
        try:
            min_lat, max_lat, min_long, max_long = get_limits(request)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            queryset = self.get_queryset().filter(coordinates__latitude__range=(min_lat, max_lat))
            queryset = queryset.filter(coordinates__longitude__range=(min_long, max_long))
            serializer = ReportSerializer(queryset, many=True)
            return Response(serializer.data)


class QuakeList(mixins.ListModelMixin,
                viewsets.GenericViewSet):

    queryset = Quake.objects.all()
    serializer_class = QuakeSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = QuakeSerializer(queryset, many=True)
        return Response(serializer.data)


class NearbyQuakesList(mixins.ListModelMixin,
                       viewsets.GenericViewSet):

    queryset = Quake.objects.all()
    serializer_class = QuakeSerializer

    def list(self, request, *args, **kwargs):
        try:
            min_lat, max_lat, min_long, max_long = get_limits(request)
            start_date, end_date = getdates(request)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            queryset = self.get_queryset().filter(coordinates__latitude__range=(min_lat, max_lat))
            queryset = queryset.filter(coordinates__longitude__range=(min_long, max_long))
            queryset = queryset.filter(timestamp__range=(start_date, end_date))
            serializer = QuakeSerializer(queryset, many=True)
            return Response(serializer.data)
