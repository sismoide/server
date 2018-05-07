from rest_framework import serializers

from map.serializers import CoordinatesSerializer
from mobile_res.models import EmergencyReport, ThreatReport, EmergencyType, ThreatType, Nonce, Report


class ReportSerializer(serializers.ModelSerializer):
    coordinates = CoordinatesSerializer()

    class Meta:
        model = Report
        fields = ('intensity', 'coordinates', 'created_on')


class WebUserChangePasswordSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    password = serializers.CharField(min_length=8)


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


class NonceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nonce
        fields = ('key',)


class ChallengeSerializer(serializers.Serializer):
    h = serializers.CharField()
