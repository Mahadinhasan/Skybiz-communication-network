from django.db import models
from django.contrib.auth.models import User
import urllib.parse
import re
import requests

def get_embed_map_link(link):
    if not link:
        return ""
    link = link.strip()
    # Extract src from iframe if user pastes the entire iframe code
    if link.startswith("<iframe"):
        match = re.search(r'src=["\']([^"\']+)["\']', link)
        if match:
            return match.group(1)
    
    # Resolve maps.app.goo.gl or goo.gl/maps redirects to find the full query/place URL
    if "maps.app.goo.gl" in link or "goo.gl/maps" in link:
        try:
            r = requests.get(link, allow_redirects=False, timeout=5)
            if r.status_code in (301, 302) and 'Location' in r.headers:
                link = r.headers['Location']
        except Exception:
            pass
            
    # Process standard google.com/maps URLs
    if "google.com/maps" in link:
        if "/embed" in link:
            return link
        coords_match = re.search(r'@([-0-9.]+),([-0-9.]+)', link)
        place_match = re.search(r'/maps/place/([^/]+)', link)
        q = ""
        if place_match:
            q = urllib.parse.unquote(place_match.group(1)).replace('+', ' ')
        if coords_match:
            lat, lon = coords_match.group(1), coords_match.group(2)
            if q:
                q = f"{q} ({lat}, {lon})"
            else:
                q = f"{lat},{lon}"
        if q:
            return f"https://maps.google.com/maps?q={urllib.parse.quote(q)}&t=&z=15&ie=UTF8&iwloc=&output=embed"
            
    # Fallback/format for maps.google query links or raw string addresses
    if link.startswith("http://") or link.startswith("https://"):
        if "maps.google" in link and "output=embed" not in link:
            return f"{link}&output=embed" if "?" in link else f"{link}?output=embed"
        return link
    return f"https://maps.google.com/maps?q={urllib.parse.quote(link)}&t=&z=15&ie=UTF8&iwloc=&output=embed"

class NewsTicker(models.Model):
    message = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.message[:50]

    class Meta:
        verbose_name = "News Ticker"
        verbose_name_plural = "News Ticker"
        ordering = ['-created_at']
        
class Package(models.Model):
    PACKAGE_TYPES = [
        ('residential', 'Residential'),
        ('business', 'Business'),
    ]
    name = models.CharField(max_length=100)
    package_type = models.CharField(max_length=50, choices=PACKAGE_TYPES)
    download_speed = models.IntegerField()
    upload_speed = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    data_limit = models.CharField(max_length=100, blank=True, null=True)
    features = models.TextField(blank=True, null=True)
    is_popular = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    reply_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.subject}"

class BusinessQuoteRequest(models.Model):
    company_name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    bandwidth = models.CharField(max_length=50)
    requirements = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company_name} - {self.contact_person}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username

class SpeedTestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    download_speed = models.FloatField()
    upload_speed = models.FloatField()
    latency = models.FloatField()
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Speed Test - {self.timestamp}"

class CarouselImage(models.Model):
    title = models.CharField(max_length=100)
    caption = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='carousel/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

class Branch(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    phone = models.CharField(max_length=30)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    website_link = models.URLField(max_length=200, blank=True, null=True)
    map_link = models.TextField(blank=True, null=True, help_text="Google Maps Embed URL (iframe src)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.map_link:
            self.map_link = get_embed_map_link(self.map_link)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.city}, {self.state}"

class FooterLocation(models.Model):
    name = models.CharField(max_length=100)
    map_link = models.TextField(help_text="Google Maps Embed URL (iframe src)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.map_link:
            self.map_link = get_embed_map_link(self.map_link)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
