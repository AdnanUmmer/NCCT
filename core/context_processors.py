from urllib.parse import urljoin
from django.conf import settings
from django.templatetags.static import static
from .models import Homepage
from enquiries.forms import EnquiryForm
from enquiries.security import issue_token


def site_content(request):
    if request.path.startswith('/admin/'):
        return {}
    content = getattr(request, '_homepage', None) or Homepage.objects.first() or Homepage(static_image='single-light-v2')
    return {'content': content, 'site_url': settings.SITE_URL,
            'page_title': content.seo_title, 'meta_description': content.seo_description,
            'canonical': settings.SITE_URL + request.path,
            'social_image': urljoin(settings.SITE_URL, content.og_image.url if content.og_image else content.image_url),
            'og_title': content.seo_title, 'og_description': content.seo_description,
            'ga4_id': content.ga4_measurement_id if settings.SITE_INDEXABLE else '',
            'noindex': not settings.SITE_INDEXABLE,
            'form': EnquiryForm(initial={'token': issue_token()})}
