from django.core.management import BaseCommand

import os

from lxml import etree

from mobile_res.models import Quake
from web.settings import BASE_DIR


def qmlparse(file):
    tree = etree.parse(file)
    root = tree.getroot()

    ns = {'q': "http://quakeml.org/xmlns/quakeml/1.2",
          'qml': "http://quakeml.org/xmlns/bed/1.2"}

    event = root.find(".//qml:event", ns)
    eventid = event.get('{http://anss.org/xmlns/catalog/0.1}eventid')

    latitude = root.find(".//qml:latitude/qml:value", ns).text
    longitude = root.find(".//qml:longitude/qml:value", ns).text
    depth = root.find(".//qml:depth/qml:value", ns).text

    magnitude = root.find(".//qml:mag/qml:value", ns).text

    timestamp = root.find(".//qml:time/qml:value", ns).text

    return eventid, latitude, longitude, depth, magnitude, timestamp


class Command(BaseCommand):

    def handle(self, *args, **options):
        # cambiar por la ubicación de los archivos QuakeML
        loc = os.path.join(BASE_DIR, 'mobile_res', 'qmls')

        files = os.listdir(path=loc)
        print(files)

        for file in files:
            eventid, latitude, longitude, depth, magnitude, timestamp = qmlparse(os.path.join(loc, file))

            print(file)

            print("eventid: " + eventid)
            print("latitude: " + latitude)
            print("longitude: " + longitude)
            print("depth: " + depth)
            print("magnitude: " + magnitude)
            print("time: " + timestamp)

            print()