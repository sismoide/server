from rest_framework import serializers

from map.models import Coordinates, Quadrant


class CoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinates
        fields = ('latitude', 'longitude')


class LocationRadiusSerializer(serializers.Serializer):
    min_coordinates = CoordinatesSerializer()
    max_coordinates = CoordinatesSerializer()

    def validate(self, attrs):
        print(attrs)
        return super(LocationRadiusSerializer, self).validate()


class QuadrantSerializer(serializers.ModelSerializer):
    min_coordinates = CoordinatesSerializer()
    max_coordinates = CoordinatesSerializer()
    map_relative_pos_x = serializers.IntegerField()
    map_relative_pos_y = serializers.IntegerField()

    class Meta:
        model = Quadrant
        fields = ('min_coordinates', 'max_coordinates', 'map_relative_pos_x', 'map_relative_pos_y', )



