from rest_framework import serializers

from mobile_res.models import Report, Coordinates


class CoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinates
        fields = ('latitude', 'longitude', 'elevation')


class IntensitySerializer(serializers.ModelSerializer):
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
