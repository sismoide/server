from datetime import datetime

from rest_framework import serializers

from mobile_res.models import Report, Coordinates, EmergencyReport, ThreatReport


class CoordinatesSerializer(serializers.ModelSerializer):
    elevation = serializers.FloatField(required=False)

    class Meta:
        model = Coordinates
        fields = ('latitude', 'longitude', 'elevation',)


class ReportSerializer(serializers.ModelSerializer):
    coordinates = CoordinatesSerializer()
    intensity = serializers.IntegerField(required=False)

    class Meta:
        model = Report
        fields = ('id', 'coordinates', 'intensity', 'created_on')

    def validate_created_on(self, value):
        print("mish")
        return value

    def validate(self, attrs):
        inte = attrs.get('created_on')
        if inte:
            print(inte)
            # raise ValidationError('Cannot update times.')

        return super().validate(attrs)

    def create(self, validated_data):
        coord_data = validated_data.pop('coordinates')
        coordinates = CoordinatesSerializer.create(CoordinatesSerializer(), validated_data=coord_data)
        try:
            report, created = Report.objects.update_or_create(
                coordinates=coordinates,
                intensity=validated_data.pop('intensity'),
                modified_on=datetime.now())
        except KeyError:
            report, created = Report.objects.update_or_create(
                coordinates=coordinates,
                modified_on=datetime.now())
        return report


class EmergencyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyReport
        fields = ('type', 'report')


class ThreatReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThreatReport
        fields = ('type', 'report')
