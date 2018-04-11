from rest_framework.routers import DefaultRouter

from mobile_res import views

router = DefaultRouter()
router.register(r'reports', views.ReportViewSet)

urlpatterns = router.urls
