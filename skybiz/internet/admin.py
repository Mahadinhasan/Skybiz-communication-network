from django.contrib import admin
from .models import Package, UserProfile, ContactMessage, BusinessQuoteRequest, SpeedTestResult

# Register your models here.
admin.site.register(Package)
admin.site.register(UserProfile)
admin.site.register(ContactMessage)
admin.site.register(BusinessQuoteRequest)
admin.site.register(SpeedTestResult)
# admin.site.register(CarouselImage)