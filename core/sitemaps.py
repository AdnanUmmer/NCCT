from django.conf import settings
from django.http import HttpResponse
from django.utils.xmlutils import SimplerXMLGenerator
from io import StringIO
from .models import ContentPage, Application
from .catalogue import public_products, public_projects
from products.models import Category


def sitemap(request):
    output = StringIO()
    xml = SimplerXMLGenerator(output, 'utf-8')
    xml.startDocument()
    xml.startElement('urlset', {'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9'})
    paths = [('/', None), ('/products/', None), ('/solutions/', None), ('/resources/', None), ('/contact/', None)]
    if public_projects().exists(): paths.append(('/projects/', None))
    for qs in (Category.objects.filter(published=True), public_products(), public_projects(), Application.objects.filter(published=True), ContentPage.objects.filter(published=True)):
        paths.extend((obj.get_absolute_url(), obj.updated_at) for obj in qs)
    if settings.SITE_INDEXABLE:
        for path, updated in paths:
            xml.startElement('url', {})
            xml.addQuickElement('loc', settings.SITE_URL + path)
            if updated: xml.addQuickElement('lastmod', updated.date().isoformat())
            xml.endElement('url')
    xml.endElement('urlset')
    return HttpResponse(output.getvalue(), content_type='application/xml')
