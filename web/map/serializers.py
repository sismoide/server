from rest_framework import serializers

from map.models import Coordinates, Quadrant


class CoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinates
        fields = ('latitude', 'longitude')


class DummySerializeR(serializers.Serializer):
    a = serializers.IntegerField()
    b = serializers.IntegerField()


class QuadrantReportSerializer(serializers.Serializer):
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    min_coordinates = CoordinatesSerializer()
    max_coordinates = CoordinatesSerializer()


class QuadrantSerializer(serializers.ModelSerializer):
    min_coordinates = CoordinatesSerializer()
    max_coordinates = CoordinatesSerializer()
    map_relative_pos_x = serializers.IntegerField()
    map_relative_pos_y = serializers.IntegerField()

    class Meta:
        model = Quadrant
        fields = ('min_coordinates', 'max_coordinates', 'map_relative_pos_x', 'map_relative_pos_y', )



