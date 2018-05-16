from rest_framework import routers

from map import views

router = routers.DefaultRouter()
router.register(r'quadrants', views.QuadrantsViewSet, base_name='quadrant')
urlpatterns = router.urls

