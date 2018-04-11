from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('mobile_res.urls', 'mobile_res'), namespace='mobile_res')),
    path('', include(('web_res.urls', 'web_res'), namespace='web_res'))
]
