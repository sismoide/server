from django.contrib import admin

from map.models import Quadrant, Landmark, LandmarkType

admin.site.register(Quadrant)
admin.site.register(Landmark)
admin.site.register(LandmarkType)
