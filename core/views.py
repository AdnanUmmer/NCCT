from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from .models import Homepage, Capability, VerifiedMetric
from products.models import Category, Product
from projects.models import Project
from enquiries.forms import EnquiryForm
from enquiries.security import issue_token

@never_cache
def home(request, form=None, form_status=200):
    content = Homepage.objects.first() or Homepage(static_image='homepg-5', image_alt='Interior with integrated ceiling and stair lighting')
    request._homepage = content
    categories = list(Category.objects.filter(published=True))
    projects = list(Project.objects.filter(featured=True, published=True)[:3])
    context = {'content':content, 'categories':categories, 'projects':projects,
        'projects_verified': bool(projects) and all(p.attribution_verified for p in projects),
        'products':Product.objects.filter(featured=True, verified=True, published=True, category__published=True).select_related('category')[:4],
        'capabilities':Capability.objects.all(), 'metrics':VerifiedMetric.objects.filter(published=True),
        'form': form if form is not None else EnquiryForm(initial={'token':issue_token()}),
        'form_error': form is not None, 'sent': request.GET.get('enquiry') == 'sent', 'site_url':settings.SITE_URL,
        'schema': {'@context':'https://schema.org','@graph':[
            {'@type':['Organization','LocalBusiness'], '@id':settings.SITE_URL+'/#organization',
             'name':content.company_name, 'url':settings.SITE_URL+'/', 'email':content.email,'telephone':content.phone,
             'address':{'@type':'PostalAddress','streetAddress':content.address,'addressLocality':'Dubai','addressCountry':'AE'}},
            {'@type':'WebSite','@id':settings.SITE_URL+'/#website','url':settings.SITE_URL+'/', 'name':content.company_name,
             'publisher':{'@id':settings.SITE_URL+'/#organization'}}]}}
    return render(request, 'home.html', context, status=form_status)

def not_found(request, exception): return render(request, '404.html', status=404)

def csrf_failure(request, reason=''):
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({'ok':False,'errors':{'__all__':[{'message':'Your session has expired. Reload the page and try again.'}]}},status=403)
    from django.template.loader import get_template
    return HttpResponse(get_template('403.html').render({'noindex': True}), status=403)

def robots(request):
    rules = 'Allow: /\nDisallow: /admin/\nDisallow: /enquiry/\n' if settings.SITE_INDEXABLE else 'Disallow: /\n'
    return HttpResponse('User-agent: *\n' + rules + 'Sitemap: ' + settings.SITE_URL + '/sitemap.xml\n', content_type='text/plain')

def server_error(request):
    # Deliberately avoids database-dependent context processors.
    from django.template.loader import get_template
    return HttpResponse(get_template('500.html').render({}), status=500)
