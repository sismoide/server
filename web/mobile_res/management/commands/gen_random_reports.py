import random
from time import sleep

import numpy as np
from django.core.management import BaseCommand

from map.models import Coordinates
from mobile_res.models import Report


class Command(BaseCommand):

    def handle(self, *args, **options):
        while True:

            # sample coordinates normal
            lat_mu, lat_sigma = -33.4378305, 0.3
            long_mu, long_sigma = -70.650449, 0.2

            lat = np.random.normal(lat_mu, lat_sigma)
            long = np.random.normal(long_mu, long_sigma)

            # forbid reports around beauchef
            forbidden_zone_min_lat = -33.488
            forbidden_zone_max_lat = -33.42
            forbidden_zone_min_long = -70.72
            forbidden_zone_max_long = -70.59

            if forbidden_zone_min_lat < lat < forbidden_zone_max_lat:
                if forbidden_zone_min_long < long < forbidden_zone_max_long:
                    print('info: omitted a report close to beauchef')
                    continue

            intens = None
            if random.uniform(0, 1) > 0.25:
                intens = int(np.random.normal(5, 1))

            r = Report.objects.create(
                coordinates=Coordinates.objects.create(
                    latitude=lat,
                    longitude=long),
                intensity=intens
            )
            print("info: generated report {}".format(r))
            sleep(30)
