from django.conf import settings
from django.http import HttpResponse
from django.utils.xmlutils import SimplerXMLGenerator
from io import StringIO
from .models import ContentPage, Application, PageContent
from .catalogue import public_products, public_projects
from products.models import Category


def sitemap(request):
    output = StringIO()
    xml = SimplerXMLGenerator(output, 'utf-8')
    xml.startDocument()
    xml.startElement('urlset', {'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9'})
    paths = [('/', None)]
    keys = {'products': '/products/', 'solutions': '/solutions/', 'resources': '/resources/', 'contact': '/contact/', 'projects': '/projects/'}
    hidden = set(PageContent.objects.filter(noindex=True).values_list('key', flat=True))
    for key, path in keys.items():
        if key in hidden or (key == 'projects' and not public_projects().exists()): continue
        row = PageContent.objects.filter(key=key).first()
        paths.append((path, row.updated_at if row else None))
    for qs in (Category.objects.filter(published=True), public_products(), public_projects(), Application.objects.filter(published=True), ContentPage.objects.filter(published=True)):
        paths.extend((obj.get_absolute_url(), obj.updated_at) for obj in qs.filter(noindex=False))
    if settings.SITE_INDEXABLE:
        for path, updated in paths:
            xml.startElement('url', {})
            xml.addQuickElement('loc', settings.SITE_URL + path)
            if updated: xml.addQuickElement('lastmod', updated.date().isoformat())
            xml.endElement('url')
    xml.endElement('urlset')
    return HttpResponse(output.getvalue(), content_type='application/xml')
