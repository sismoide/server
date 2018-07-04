from rest_framework import serializers

from map.models import Coordinates, Quadrant, ReportQuadrantAggregationSlice, Landmark, LandmarkType


class CoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinates
        fields = ('latitude', 'longitude')


class DummySerializeR(serializers.Serializer):
    a = serializers.IntegerField()
    b = serializers.IntegerField()


class ReportQuadrantAggregationSliceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportQuadrantAggregationSlice
        fields = ('start_timestamp',
                  'end_timestamp',
                  'report_total_count',
                  'report_w_intensity_count',
                  'intensity_sum')


class QuadrantSerializer(serializers.ModelSerializer):
    min_coordinates = CoordinatesSerializer()
    max_coordinates = CoordinatesSerializer()
    map_relative_pos_x = serializers.IntegerField()
    map_relative_pos_y = serializers.IntegerField()

    class Meta:
        model = Quadrant
        fields = ('min_coordinates', 'max_coordinates', 'map_relative_pos_x', 'map_relative_pos_y', )


class LandmarkSerializer(serializers.ModelSerializer):
    coordinates = CoordinatesSerializer()
    type = serializers.StringRelatedField()

    class Meta:
        model = Landmark
        fields = '__all__'


class LandmarkTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandmarkType
        fields = '__all__'
