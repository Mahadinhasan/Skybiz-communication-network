from django.urls import path,re_path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('packages/', views.packages, name='packages'),
    path('services/', views.services, name='services'),
    path('business/', views.business, name='business'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('admin/', views.admin_panel, name='admin_panel'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('speedtest/ping/', views.speedtest_ping, name='speedtest_ping'),
    path('speedtest/download/', views.speedtest_download, name='speedtest_download'),
    path('speedtest/upload/', views.speedtest_upload, name='speedtest_upload'),
    path('speedtest/save/', views.speedtest_save, name='speedtest_save'),
    path('speedtest/', views.speed_test_view, name='speed_test'),
    path('faq/', views.faq, name='faq'),
    re_path(r'^.*$', views.custom_404_view, name='custom_404'),
]
