from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from web.settings import MOBILE_PATH_PREFIX, WEB_PATH_PREFIX, MAP_PATH_PREFIX

urlpatterns = [
    path('', TemplateView.as_view(template_name='docs/docs.html'), name='index'),
    path('admin/', admin.site.urls),
    path('{}/'.format(MOBILE_PATH_PREFIX), include(('mobile_res.urls', 'mobile_res'), namespace='mobile_res')),
    path('{}/'.format(WEB_PATH_PREFIX), include(('web_res.urls', 'web_res'), namespace='web_res')),
    path('{}/'.format(MAP_PATH_PREFIX), include(('map.urls', 'map'), namespace='map')),
]
