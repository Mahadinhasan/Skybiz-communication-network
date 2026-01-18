from django.urls import path
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
    path('home-speed-test/', views.home_speed_test, name='home_speed_test'),
    path('faq/', views.faq, name='faq'),
]