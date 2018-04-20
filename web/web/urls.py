from django.contrib import admin
from django.urls import path, include

from web.settings import MOBILE_PATH_PREFIX, WEB_PATH_PREFIX

urlpatterns = [
    path('admin/', admin.site.urls),
    path('{}/'.format(MOBILE_PATH_PREFIX), include(('mobile_res.urls', 'mobile_res'), namespace='mobile_res')),
    path('{}/'.format(WEB_PATH_PREFIX), include(('web_res.urls', 'web_res'), namespace='web_res'))
]
