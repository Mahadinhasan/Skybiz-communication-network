from django.contrib import admin
from django.urls import path, include
from internet.views import custom_404_view
from django.conf import settings
from django.conf.urls.static import static

handler404 = custom_404_view

urlpatterns = [
    path('admin_developer/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path('', include('internet.urls')),
]

