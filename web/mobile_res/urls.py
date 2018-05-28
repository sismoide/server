import schedule
import time
from django.urls import path
from rest_framework.routers import DefaultRouter

from mobile_res import views
from mobile_res.management.commands.getquakes import get_quakes
from web.utils import async

router = DefaultRouter()
router.register(r'reports', views.ReportViewSet)
router.register(r'nearbyreports', views.NearbyReportsList, base_name='nearby-reports')
router.register(r'threats', views.ThreatReportViewSet)
router.register(r'emergencies', views.EmergencyReportViewSet)
router.register(r'quakes', views.QuakeList)
router.register(r'nearbyquakes', views.NearbyQuakesList, base_name='nearby-quakes')
router.register(r'nonce', views.NonceViewSet)


urlpatterns = router.urls
urlpatterns += [
    path('challenge/', views.ValidateChallengeAPIView.as_view(), name='challenge'),
]

"""
This piece of code is executed only once, at the beginning.
"""


@async
def check_quakes():
    #print("Started monitoring files")

    schedule.every(30).seconds.do(get_quakes)

    while True:
        schedule.run_pending()
        time.sleep(30)


check_quakes()
