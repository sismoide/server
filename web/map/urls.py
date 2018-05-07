from django.urls.conf import path
from rest_framework import routers
from rest_framework.authtoken import views as auth_views

from map import views

"""
router = routers.DefaultRouter()
router.register(r'reports', views.ReportList)
router.register(r'emergencies', views.EmergencyList)
router.register(r'threats', views.ThreatList)
urlpatterns = router.urls
urlpatterns += [
    path(r'change_pass', views.WebUserChangePassword.as_view(), name='web_user-change_pass'),
    path(r'get_token', auth_views.obtain_auth_token, name='web_user-get_token')
]

"""
router = routers.DefaultRouter()
router.register(r'quadrants', views.QuadrantsViewSet, base_name='quadrant')
urlpatterns = router.urls

