import datetime as dt
import os
import uuid
from math import cos, radians

from lxml import etree

from map.models import Coordinates
from mobile_res.models import MobileUser
from web.settings import QUAKEML_DIR


def random_username():
    return str(uuid.uuid5(uuid.uuid4(), "django:user"))[:11]


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


# Adds quakes to database from files
def get_quakes():
    from mobile_res.models import Quake

    # location of QuakeML files
    files = os.listdir(path=QUAKEML_DIR)

    # process all files in folder
    for file in files:
        eventid, latitude, longitude, depth, magnitude, timestamp, creation_time = qmlparse(
            os.path.join(QUAKEML_DIR, file))

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
        file_path = os.path.join(QUAKEML_DIR, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(e)


# given a request with latitude, longitude, and radius, returns min and max
# coordinates for surrounding square
def get_limits(request):
    # in kilometers
    radius = float(request.query_params.get('rad', "10.0"))

    # length of 1 degree at the equator (latitude and longitude)
    km_p_deg_lat = 110.57
    km_p_deg_long = 111.32

    current_lat = float(request.query_params.get('latitude', "50.0"))
    current_long = float(request.query_params.get('longitude', "50.0"))

    min_lat = current_lat - (radius/km_p_deg_lat)
    max_lat = current_lat + (radius/km_p_deg_lat)

    # length of 1 longitude degree (varies with latitude)
    deg_length = cos(radians(current_lat)) * km_p_deg_long

    min_long = current_long - (radius/deg_length)
    max_long = current_long + (radius/deg_length)

    return min_lat, max_lat, min_long, max_long


# given a date type ("start"/"end") and a default date, gets a date from request parameters.
def get_date_from_request(request, date_type, default):
    date = request.query_params.get(date_type, default)
    return dt.datetime.strptime(date, "%Y-%m-%dT%H:%M")


# gets start and end dates from request
def get_start_and_end_dates(request):
    start_date = get_date_from_request(request, 'start', "1918-01-01T00:00")
    end_date = get_date_from_request(request, 'end', "2100-12-31T23:59")
    return start_date, end_date


def add_points_to_user(user, points):
    """
    Add points to user.
    :param user: USER whom the points are going to be added.
    :param points: ammount of points (integer) to be added.
    :return:
    """
    try:
        m = MobileUser.objects.get(user=user)
        m.points += points
        m.save()
        return 0
    except MobileUser.DoesNotExist:
        print("warning: Mobile user not found for auth user. Avoiding points increase.")
        return -1
