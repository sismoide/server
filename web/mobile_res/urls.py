from django.urls import path
from rest_framework.routers import DefaultRouter

from mobile_res import views

router = DefaultRouter()
router.register(r'reports', views.ReportViewSet)
router.register(r'threats', views.ThreatReportViewSet)
router.register(r'emergencies', views.EmergencyReportViewSet)
router.register(r'nonce', views.NonceViewSet)


urlpatterns = router.urls
urlpatterns += [
    path('challenge', views.ValidateChallengeAPIView.as_view(), name='challenge'),
]

"""
This piece of code is executed only once, at the beginning.
"""
