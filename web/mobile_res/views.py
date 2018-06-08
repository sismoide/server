from rest_framework import viewsets, mixins, status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from mobile_res.models import EmergencyReport, ThreatReport, Quake, Nonce, MobileUser, Report
from mobile_res.serializers import ReportCreateSerializer, EmergencyReportSerializer, ThreatReportSerializer, \
    ReportPatchSerializer, QuakeSerializer
from mobile_res.utils import get_limits, get_start_and_end_dates
from web.settings import HASH_CLASS
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

    def create(self, request, *args, **kwargs):
        ret = super().create(request, *args, **kwargs)
        if request.user.is_authenticated:
            # Add information about user whom created the report
            if ret.status_code == 201:
                r = Report.objects.get(pk=ret.data['id'])
                r.creator = request.user
                r.save()
        return ret

    def update(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            # maybe isn't necessary but just in case
            raise Exception("Patch call not authenticated")
        try:
            # get report id from URL call
            pk = request.path.split("/")[-2]
            # recover report
            r = Report.objects.get(pk=pk)
            if r.creator:
                # if report is signed
                if r.creator == request.user:
                    # and is signed by same user
                    return super().update(request, *args, **kwargs)
                else:
                    # and is signed by other user
                    return Response({"Tried to patch other user's report"}, status=status.HTTP_403_FORBIDDEN)
        except IndexError:
            print("warning: Tried to patch with invalid url {}".format(request.path))
        except Report.DoesNotExist:
            print("warning: Tried to patch unexistant report id={}".format(pk))

        # if report's not signed or exception
        return super().update(request, *args, **kwargs)


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
        try:
            nonce_key = request.META['HTTP_AUTHORIZATION']
        except KeyError:
            # HTTP_AUTHORIZATION header not found
            return Response({}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            # 'invalid scheme'
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
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
            start_date, end_date = get_start_and_end_dates(request)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            queryset = self.get_queryset().filter(coordinates__latitude__range=(min_lat, max_lat))
            queryset = queryset.filter(coordinates__longitude__range=(min_long, max_long))
            queryset = queryset.filter(timestamp__range=(start_date, end_date))
            serializer = QuakeSerializer(queryset, many=True)
            return Response(serializer.data)
