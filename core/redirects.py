# Only map genuine NCCT pages. LumoTubo case studies are not NCCT projects.
LEGACY_REDIRECTS = {
    '/en/index.html': '/',
    '/en/contact-2/index.html': '/contact/',
    '/en/Real/lightsfeatures.html': '/solutions/',
    '/en/do-pobrania-2/products.html': '/resources/',
}


from django.http import HttpResponsePermanentRedirect, Http404
from products.models import Category

CATEGORY_LEGACY = ['indoor_lights', 'Outdoor_lights', 'Decorative_lights', 'industrial_lights', 'professional_lights']

def category_redirect(request, legacy):
    obj = Category.objects.filter(published=True, source_url=f'https://ncctdxb.com/en/Real/{legacy}.html').first()
    if not obj: raise Http404
    return HttpResponsePermanentRedirect(obj.get_absolute_url())
