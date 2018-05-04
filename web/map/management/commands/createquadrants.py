from django.core.management import BaseCommand

from map.models import Quadrant, Coordinates
from web import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        Create quadrants based on quadrant and country parameters set in Settings.py

        :param args:
        :param options:
        :return:
        """
        # axis x == longitude
        # axis y == latitude

        current_long = settings.CHILE_MIN_LONG
        current_lat = settings.CHILE_MIN_LAT
        x = 0
        y = 0

        while current_lat < settings.CHILE_MAX_LAT:
            # iterate from south to north
            while current_long < settings.CHILE_MAX_LONG:
                # build quadrants from west to east

                min_corner_coord = Coordinates.objects.create(
                    longitude=current_long,
                    latitude=current_lat
                )
                current_long += settings.QUADRANT_LONG_DELTA

                max_corner_coord = Coordinates.objects.create(
                    longitude=current_long,
                    latitude=current_lat
                )

                quad = Quadrant.objects.create(
                    min_coordinates=min_corner_coord,
                    max_coordinates=max_corner_coord,
                    map_relative_pos_x=x,
                    map_relative_pos_y=y
                )
                print(quad)
                # finally
                x += 1

            # finally
            print("info: finished row {}".format(y))
            current_long = settings.CHILE_MIN_LAT
            current_lat += settings.QUADRANT_LEN_DELTA
            x = 0
            y += 1
