import math

from django.db import models


class Coordinates(models.Model):
    """
    latitude and longitude specified in Decimal Degrees (xxx.ddddddddd)
    elevation specified in Meters above sea.
    """
    latitude = models.DecimalField(max_digits=13, decimal_places=10)
    longitude = models.DecimalField(max_digits=13, decimal_places=10)

    def __str__(self):
        return "{}, {}".format(self.latitude, self.longitude)

    def distance(self, other_coordinates):
        """
        Calculate distance between 2 coordinates.
        :param other_coordinates: Coordinates instance that are comparing with.
        :return: cartesian distance
        """
        # pythagoras's theorem
        return math.sqrt(
            (other_coordinates.latitude - self.latitude) ^ 2 +
            (other_coordinates.longitude - self.longitude) ^ 2
        )

    def __eq__(self, other):
        return self.latitude == other.latitude and self.longitude == other.longitude

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return self.latitude > other.latitude and self.longitude > other.longitude

    def __le__(self, other):
        return not self.__gt__(other)

    def __lt__(self, other):
        return self.latitude < other.latitude or self.longitude < other.longitude

    def __ge__(self, other):
        return not self.__lt__(other)


class Quadrant(models.Model):
    """
    Chile is democratized in quadrilateral quadrants of size specified in
    geographical coordinates (web/settings.py)
    This model instances are generated through 'createquadrants' command with
    parameters specified in settings.py.
    Also, a dump is saved in 'quadrants.json' fixture
    (load with manage.py loaddata <fixture>).
    """
    # todo: guardar fixture despues
    min_coordinates = models.ForeignKey(Coordinates, on_delete=models.PROTECT, related_name='quadrant_min')
    max_coordinates = models.ForeignKey(Coordinates, on_delete=models.PROTECT, related_name='quadrant_max')
    map_relative_pos_x = models.IntegerField()
    map_relative_pos_y = models.IntegerField()

    def __str__(self):
        return "Quadrant:\n relative pos ({}, {});\n coordinates of edges [({}), ({})]".format(
            self.map_relative_pos_x,
            self.map_relative_pos_y,
            self.min_coordinates,
            self.max_coordinates
        )

    def __eq__(self, other):
        return self.min_coordinates == other.min_coordinates and self.max_coordinates == other.max_coordinates


class ReportQuadrantAggregationSlice(models.Model):
    """
    Slice of time aggregation of reports in a specified quadrant.
    This slices are used to calculate mean intensity in a quadrant.

    Usually a query will include many slices that will be reduced into a set of values.
    """
    start_timestamp = models.DateTimeField()
    end_timestamp = models.DateTimeField()
    quadrant = models.ForeignKey(Quadrant, on_delete=models.CASCADE)
    report_total_count = models.IntegerField()
    report_w_intensity_count = models.IntegerField()
    intensity_sum = models.IntegerField()
