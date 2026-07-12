from .models import NewsTicker, FooterLocation, CarouselImage

def global_context(request):
    return {
        'news_ticker': NewsTicker.objects.filter(is_active=True),
        'footer_locations': FooterLocation.objects.filter(is_active=True),
        'carousel_images': CarouselImage.objects.filter(is_active=True)[:5],
    }
