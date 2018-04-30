from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='docs/docs.html'), name='index'),
    path('admin/', admin.site.urls),
    path('mobile/', include(('mobile_res.urls', 'mobile_res'), namespace='mobile_res')),
    path('web/', include(('web_res.urls', 'web_res'), namespace='web_res'))
]
