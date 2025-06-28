from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('api.v1.auth.urls', namespace='auth')),
    path('api/v1/timetable/', include('api.v1.timetable.urls', namespace='timetable')),
    path('api/v1/homeworks/', include('api.v1.homeworks.urls', namespace='homeworks'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)