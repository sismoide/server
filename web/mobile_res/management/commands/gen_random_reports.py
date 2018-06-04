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
            lat_mu, lat_sigma = -33.44082645067171, 0.11
            long_mu, long_sigma = -70.6684904624866, 0.07

            lat = np.random.normal(lat_mu, lat_sigma)
            long = np.random.normal(long_mu, long_sigma)

            intens = None
            if random.uniform(0, 1) > 0.25:
                intens = int(np.random.normal(5, 1))

            Report.objects.create(
                coordinates=Coordinates.objects.create(
                    latitude=lat,
                    longitude=long),
                intensity=intens
            )
            sleep(5)
