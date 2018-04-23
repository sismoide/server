from rest_framework import serializers

from mobile_res.models import Report, Coordinates, EmergencyReport, ThreatReport, EmergencyType, ThreatType


class CoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinates
        fields = ('latitude', 'longitude', 'elevation')


class ReportSerializer(serializers.ModelSerializer):
    coordinates = CoordinatesSerializer()

    class Meta:
        model = Report
        fields = ('intensity', 'coordinates', 'created_on')


class EmergencyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyType
        fields = ('title',)


class EmergencySerializer(serializers.ModelSerializer):
    type = EmergencyTypeSerializer()
    report = ReportSerializer()

    class Meta:
        model = EmergencyReport
        fields = ('type', 'report', 'timestamp')


class ThreatTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThreatType
        fields = ('title',)


class ThreatSerializer(serializers.ModelSerializer):
    type = ThreatTypeSerializer()
    report = ReportSerializer()

    class Meta:
        model = ThreatReport
        fields = ('type', 'report', 'timestamp')
