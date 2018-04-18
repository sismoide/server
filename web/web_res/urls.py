from django.urls.conf import path
from rest_framework import routers

from web_res import views

router = routers.DefaultRouter()
router.register(r'reports', views.ReportList)

urlpatterns = [
    path(r'change_pass', views.WebUserChangePassword.as_view(), name='web_user-change_pass'),
]
urlpatterns += router.urls
