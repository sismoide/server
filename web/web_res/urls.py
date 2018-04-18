from django.urls.conf import path
from rest_framework import routers
from rest_framework.authtoken import views as auth_views

from web_res import views

router = routers.DefaultRouter()
router.register(r'reports', views.ReportList)

urlpatterns = [
    path(r'change_pass', views.WebUserChangePassword.as_view(), name='web_user-change_pass'),
    path(r'api-token-auth', auth_views.obtain_auth_token, name='web_user-get_token')
]
urlpatterns += router.urls
