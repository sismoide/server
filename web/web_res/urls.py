from rest_framework import routers
from web_res import views


router = routers.DefaultRouter()
router.register(r'reports', views.ReportList)
urlpatterns = router.urls
