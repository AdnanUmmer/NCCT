from pathlib import Path
from urllib.parse import urlencode, urljoin
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import never_cache
from .models import Application, Capability, ContentPage, Resource, Homepage
from products.models import Category, Product
from projects.models import Project


def public_products():
    return Product.objects.filter(published=True, verified=True, category__published=True).select_related('category')


def public_projects():
    return Project.objects.filter(published=True, attribution_verified=True)


def page(request, template, title, description, context=None, obj=None, crumbs=None, schema_type='WebPage'):
    context = context or {}
    title = (getattr(obj, 'seo_title', '') or title) + ' | NCCT'
    description = getattr(obj, 'seo_description', '') or description
    canonical = getattr(obj, 'canonical_url', '') or settings.SITE_URL + request.path
    crumbs = [('Home', '/')] + (crumbs or [])
    graph = [{'@type': schema_type, 'name': title, 'description': description, 'url': canonical},
             {'@type': 'BreadcrumbList', 'itemListElement': [
                 {'@type': 'ListItem', 'position': i + 1, 'name': label, 'item': settings.SITE_URL + path}
                 for i, (label, path) in enumerate(crumbs)]}]
    if schema_type == 'Product' and obj:
        graph[0]['image'] = urljoin(settings.SITE_URL, obj.image_url)
        if obj.model_reference: graph[0]['model'] = obj.model_reference
    context.update(page_title=title, meta_description=description, canonical=canonical,
                   breadcrumbs=crumbs, schema={'@context': 'https://schema.org', '@graph': graph})
    if obj and hasattr(obj, 'image_url'):
        context['social_image'] = urljoin(settings.SITE_URL, obj.image_url)
    return render(request, template, context)


@never_cache
def products(request, category_slug=None):
    category = get_object_or_404(Category, published=True, slug=category_slug) if category_slug else None
    qs = public_products()
    if category: qs = qs.filter(category=category)
    available = qs
    filters = {}
    for key in ['mounting_type', 'ip_rating', 'colour_temperature']:
        values = list(available.exclude(**{key: ''}).order_by(key).values_list(key, flat=True).distinct())
        if values: filters[key] = values
    selected_category = request.GET.get('category', '')
    q = request.GET.get('q', '').strip()[:200]
    if not category and selected_category: qs = qs.filter(category__slug=selected_category)
    if q: qs = qs.filter(Q(name__icontains=q) | Q(model_reference__icontains=q) | Q(description__icontains=q) | Q(category__name__icontains=q))
    for key in filters:
        value = request.GET.get(key, '')
        if value: qs = qs.filter(**{key: value})
    sort = request.GET.get('sort', '')
    qs = qs.order_by('name', 'pk') if sort == 'name' else qs.order_by('order', 'pk')
    pager = Paginator(qs, 12).get_page(request.GET.get('page'))
    params = request.GET.copy(); params.pop('page', None)
    title = category.name if category else 'Lighting products'
    context = {'listing': pager, 'category': category, 'catalogue_categories': Category.objects.filter(published=True),
               'filters': filters, 'q': q, 'selected_category': selected_category, 'sort': sort,
               'query_string': params.urlencode(), 'heading': title}
    if request.GET: context['noindex'] = True
    return page(request, 'catalogue/products.html', title,
                category.description if category else 'Discover NCCT lighting by category, model and technical characteristics. Browse product details and download available datasheets.',
                context, category, [('Products', '/products/')] + ([(category.name, category.get_absolute_url())] if category else []), 'CollectionPage')


@never_cache
def product_detail(request, category_slug, slug):
    obj = get_object_or_404(public_products().prefetch_related('gallery', 'specification_rows', 'features'), slug=slug, category__slug=category_slug)
    return page(request, 'catalogue/product.html', obj.name, obj.description,
                {'product': obj, 'documents': obj.documents.filter(published=True),
                 'applications': obj.applications.filter(published=True),
                 'related': public_products().filter(category=obj.category).exclude(pk=obj.pk)[:3],
                 'related_projects': public_projects().filter(products=obj)}, obj,
                [('Products', '/products/'), (obj.category.name, obj.category.get_absolute_url()), (obj.name, obj.get_absolute_url())], 'Product')


@never_cache
def projects(request):
    qs = public_projects()
    sectors = list(qs.exclude(application='').order_by('application').values_list('application', flat=True).distinct())
    sector = request.GET.get('sector', '')
    if sector: qs = qs.filter(application=sector)
    return page(request, 'catalogue/projects.html', 'Projects', 'Explore published NCCT lighting projects and discuss your project requirements with our team.',
                {'listing': Paginator(qs, 9).get_page(request.GET.get('page')), 'sectors': sectors, 'sector': sector, 'query_string': urlencode({'sector': sector}), 'noindex': bool(request.GET) or not settings.SITE_INDEXABLE},
                crumbs=[('Projects', '/projects/')], schema_type='CollectionPage')


@never_cache
def project_detail(request, slug):
    obj = get_object_or_404(public_projects().prefetch_related('gallery'), slug=slug)
    return page(request, 'catalogue/project.html', obj.title, obj.description,
                {'project': obj, 'related_products': public_products().filter(projects=obj)}, obj,
                [('Projects', '/projects/'), (obj.title, obj.get_absolute_url())], 'CreativeWork')


@never_cache
def solutions(request, slug=None):
    if slug:
        obj = get_object_or_404(Application, published=True, slug=slug)
        return page(request, 'catalogue/solution.html', obj.name + ' solutions', 'Explore ' + obj.name.lower() + ' applications and connected product categories with NCCT. ' + obj.description,
                    {'solution': obj, 'solution_categories': obj.categories.filter(published=True),
                     'related_products': public_products().filter(applications=obj),
                     'related_projects': public_projects().filter(applications=obj)}, obj,
                    [('Solutions', '/solutions/'), (obj.name, obj.get_absolute_url())])
    return page(request, 'catalogue/solutions.html', 'Lighting solutions', 'Explore indoor, outdoor, decorative, industrial and professional lighting with NCCT.',
                {'applications': Application.objects.filter(published=True)}, crumbs=[('Solutions', '/solutions/')], schema_type='CollectionPage')


@never_cache
def resources(request):
    qs = Resource.objects.filter(published=True).select_related('category')
    types = [(key, label) for key, label in Resource.TYPES if qs.filter(document_type=key).exists()]
    kind = request.GET.get('type', '')
    if kind: qs = qs.filter(document_type=kind)
    return page(request, 'catalogue/resources.html', 'Resources & downloads', 'Download available lighting datasheets and technical documents supplied on the NCCT website.',
                {'documents': qs, 'resource_types': types, 'selected_type': kind, 'noindex': bool(request.GET) or not settings.SITE_INDEXABLE}, crumbs=[('Resources', '/resources/')], schema_type='CollectionPage')


def download(request, slug):
    obj = get_object_or_404(Resource, slug=slug, published=True)
    try:
        if obj.file:
            stream = obj.file.open('rb')
            filename = Path(obj.file.name).name
        else:
            filename = obj.bundled_file
            if Path(filename).name != filename or not filename.endswith('.pdf'): raise Http404
            stream = (settings.BASE_DIR / 'static' / 'documents' / filename).open('rb')
    except (OSError, ValueError):
        raise Http404('Document unavailable')
    response = FileResponse(stream, as_attachment=True, filename=filename, content_type='application/pdf')
    response['X-Content-Type-Options'] = 'nosniff'
    response['X-Robots-Tag'] = 'noindex'
    response['Cache-Control'] = 'private, no-store'
    return response


@never_cache
def content_page(request, slug):
    obj = get_object_or_404(ContentPage, slug=slug, published=True)
    context = {'page': obj, 'capabilities': Capability.objects.all() if slug == 'about' else []}
    return page(request, 'catalogue/page.html', obj.title, obj.introduction, context, obj, [(obj.title, obj.get_absolute_url())])


@never_cache
def contact(request):
    return page(request, 'catalogue/contact.html', 'Contact NCCT', 'Contact the NCCT team in Business Bay, Dubai. Discuss lighting products, technical information or your project requirements.', crumbs=[('Contact', '/contact/')], schema_type='ContactPage')
