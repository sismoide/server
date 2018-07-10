from django.urls import path
from rest_framework import routers

from map import views

router = routers.DefaultRouter()
router.register(r'quadrants', views.QuadrantsViewSet, base_name='quadrant')
router.register(r'landmarks', views.LandmarkViewSet)
router.register(r'landmark_types', views.LandmarkTypeViewSet, base_name='landmark_type')
urlpatterns = router.urls

urlpatterns += [
    path('quadrant_reports/', views.GetQuadrantReportAggregation.as_view(), name='get_quadrant_report_aggregation'),
]
