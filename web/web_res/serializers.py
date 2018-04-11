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
