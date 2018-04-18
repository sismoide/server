from rest_framework import routers

from web_res import views

router = routers.DefaultRouter()
router.register(r'reports', views.ReportList)
router.register(r'emergencies', views.EmergencyList)
router.register(r'threats', views.ThreatList)
urlpatterns = router.urls
