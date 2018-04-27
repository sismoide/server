from rest_framework.routers import DefaultRouter

from mobile_res import views

router = DefaultRouter()
router.register(r'reports', views.ReportViewSet)
router.register(r'nearbyreports', views.NearbyReportsList, base_name='nearby-reports')
router.register(r'threats', views.ThreatReportViewSet)
router.register(r'emergencies', views.EmergencyReportViewSet)
router.register(r'quakes', views.QuakeList)
router.register(r'nearbyquakes', views.NearbyQuakesList, base_name='nearby-quakes')

urlpatterns = router.urls
