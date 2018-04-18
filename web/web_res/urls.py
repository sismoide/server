from rest_framework import routers
from web_res import views
from rest_framework.authtoken import views as auth_views
from django.urls import re_path

router = routers.DefaultRouter()
router.register(r'reports', views.ReportList)
router.register(r'emergencies', views.EmergencyList)
router.register(r'threats', views.ThreatList)
urlpatterns = router.urls

urlpatterns = [
    re_path(r'^api-token-auth/', auth_views.obtain_auth_token)
]

urlpatterns += router.urls

