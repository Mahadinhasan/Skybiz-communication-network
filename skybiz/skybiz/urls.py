from django.contrib import admin
from django.urls import path, include
from internet.views import custom_404_view

handler404 = custom_404_view

urlpatterns = [
    path('admin_developer/', admin.site.urls),
    path('', include('internet.urls')),
]
