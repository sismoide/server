from django.urls.conf import path
from rest_framework import routers
from web_res import views
from rest_framework.authtoken import views as auth_views
from django.urls import re_path

router = routers.DefaultRouter()
router.register(r'reports', views.ReportList)

urlpatterns = [
    path(r'change_pass', views.WebUserChangePassword.as_view(), name='web_user-change_pass'),
]
urlpatterns += router.urls

urlpatterns = [
    re_path(r'^api-token-auth/', auth_views.obtain_auth_token)
]

urlpatterns += router.urls

