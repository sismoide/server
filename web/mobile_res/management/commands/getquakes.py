import datetime as dt
import os
import schedule
import time

from django.core.management import BaseCommand

from lxml import etree

from map.models import Coordinates
from mobile_res.models import Quake
from web.settings import BASE_DIR


# get quake data from QuakeML file
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

    creation_time = root.find(".//qml:creationTime", ns).text

    return eventid, float(latitude), float(longitude), float(depth), \
           float(magnitude), dt.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ"), \
           dt.datetime.strptime(creation_time, "%Y-%m-%dT%H:%M:%S.%fZ")


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Started monitoring files")

        # check every minute for new quakes
        schedule.every().minute.do(get_quakes)

        while True:
            schedule.run_pending()
            time.sleep(1)


#Adds quakes to database from files
def get_quakes():
    print("Getting quakes")
    # location of QuakeML files
    loc = os.path.join(BASE_DIR, 'mobile_res', 'qmls')
    files = os.listdir(path=loc)

    #process all files in folder
    if not files:
        print("No files")
    for file in files:
        eventid, latitude, longitude, depth, magnitude, timestamp, creation_time = qmlparse(os.path.join(loc, file))

        print("eventid: " + eventid)
        print("latitude: " + str(latitude))
        print("longitude: " + str(longitude))
        print("depth: " + str(depth))
        print("magnitude: " + str(magnitude))
        print("timestamp: " + timestamp.strftime("%Y-%m-%dT%H:%M:%S"))
        print("creation time: " + creation_time.strftime("%Y-%m-%dT%H:%M:%S"))
        print()

        coords = Coordinates.objects.create(
            latitude=latitude,
            longitude=longitude
        )

        # check if quake already exists, and add it to database if not
        quake, created = Quake.objects.get_or_create(
            eventid=eventid,
            defaults={'coordinates': coords,
                      'depth': depth,
                      'magnitude': magnitude,
                      'timestamp': timestamp,
                      'creation_time': creation_time}
        )

        # if quake already exists, update with new data if appropiate
        if not created:

            original_creation = quake.creation_time.replace(tzinfo=None)
            new_creation = creation_time
            # update only if data is newer
            if new_creation > original_creation:
                quake, created = Quake.objects.update_or_create(
                    eventid=eventid,
                    defaults={'creation_time': new_creation,
                              'coordinates': coords,
                              'depth': depth,
                              'magnitude': magnitude,
                              'timestamp': timestamp}
                )

    # remove all QuakeML files
    for file in files:
        file_path = os.path.join(loc, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(e)
