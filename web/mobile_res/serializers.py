from django.utils import timezone
from rest_framework import serializers

from map.serializers import CoordinatesSerializer
from mobile_res.models import Report, EmergencyReport, ThreatReport, Quake


class ReportCreateSerializer(serializers.ModelSerializer):
    coordinates = CoordinatesSerializer()
    intensity = serializers.IntegerField(required=False)
    created_on = serializers.DateTimeField(default=timezone.now())

    class Meta:
        model = Report
        fields = ('id', 'coordinates', 'intensity', 'created_on')

    def create(self, validated_data):
        # workaround for allowing nested creation of coordinates inside report
        coord_data = validated_data.pop('coordinates')
        coordinates = CoordinatesSerializer.create(CoordinatesSerializer(), validated_data=coord_data)
        try:
            report, created = Report.objects.update_or_create(
                coordinates=coordinates,
                intensity=validated_data.pop('intensity'),
                modified_on=timezone.now(),
                created_on=validated_data.pop('created_on'))
        except KeyError:
            report, created = Report.objects.update_or_create(
                coordinates=coordinates,
                modified_on=timezone.now(),
                created_on=validated_data.pop('created_on'))
        return report


class ReportPatchSerializer(serializers.ModelSerializer):
    intensity = serializers.IntegerField(required=False)

    class Meta:
        model = Report
        fields = ('id', 'intensity')


class EmergencyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyReport
        fields = ('type', 'report')


class ThreatReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThreatReport
        fields = ('type', 'report')


class QuakeSerializer(serializers.ModelSerializer):
    coordinates = CoordinatesSerializer()

    class Meta:
        model = Quake
        fields = ('timestamp', 'coordinates', 'depth', 'magnitude')
