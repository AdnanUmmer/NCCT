from pathlib import Path
from urllib.parse import urlencode, urljoin
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import FileResponse, Http404
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import never_cache
from .models import Application, Capability, ContentPage, PageContent, Resource, Homepage, VerifiedMetric
from .page_defaults import PAGE_DEFAULTS
from .editorial import GUIDES, GUIDE_BY_SLUG, FAQS, solution_copy, application_links
from products.models import Category, Product
from projects.models import Project


def public_products():
    return Product.objects.filter(published=True, verified=True, category__published=True).select_related('category')


def public_projects():
    return Project.objects.filter(published=True)


def nav_categories():
    return Category.objects.filter(published=True).annotate(
        product_total=Count('product', filter=Q(product__published=True, product__verified=True), distinct=True))


def page_content(key):
    """Editable copy for a listing page; blank text fields fall back to the starter copy."""
    defaults = PAGE_DEFAULTS.get(key, {})
    pc, _ = PageContent.objects.get_or_create(key=key, defaults=defaults)
    for field in ('eyebrow', 'heading', 'intro', 'seo_title', 'seo_description', 'cta_eyebrow', 'cta_heading', 'cta_text'):
        if not getattr(pc, field) and defaults.get(field):
            setattr(pc, field, defaults[field])
    revisions = {
        'projects': ('Lighting in Context.', 'Explore lighting references that demonstrate how illumination can shape interiors, outdoor spaces, architectural features and landscaped environments.'),
        'solutions': ('Lighting Solutions for Every Environment.', 'Explore lighting applications for contemporary interiors, outdoor architecture, commercial spaces, industrial environments and specialist settings.'),
        'resources': ('Technical Resources & Lighting Knowledge.', 'Explore lighting product documentation and essential technical information to support informed product selection.'),
        'contact': ("Let's Discuss Your Lighting Requirements.", 'Whether you are exploring products, reviewing technical details or planning lighting for a particular environment, share your requirements with the NCCT team.'),
        'products': ('Lighting Products', 'Browse by category, compare available technical details and find the right product for your application.'),
    }
    if key in revisions:
        for field, value in zip(('heading', 'intro'), revisions[key]):
            if getattr(pc, field) == defaults.get(field):
                setattr(pc, field, value)
    return pc


def _abs(url):
    return urljoin(settings.SITE_URL + '/', url)


def page(request, template, title, description, context=None, obj=None, crumbs=None, schema_type='WebPage', pc=None, items=None):
    """Render a public page with SEO, social and structured data taken from the editable record."""
    context = context or {}
    seo = obj or pc
    site = context.get('content') or Homepage.objects.first()
    company = (site.company_name if site else '') or 'NCCT'
    seo_title = getattr(seo, 'seo_title', '') or title
    title = seo_title if seo_title.endswith(company) else f'{seo_title} | {company}'
    description = getattr(seo, 'seo_description', '') or Truncator(strip_tags(description or '')).chars(158) or f'{seo_title} — architectural and professional lighting from {company}, Dubai.'
    if not getattr(seo, 'seo_description', '') and len(description) < 80:
        description = (description.rstrip('. ') + '. ' if description else '') + f'{seo_title} from {company}, architectural and professional lighting in Dubai, UAE.'
    description = Truncator(description).chars(160)
    canonical = getattr(obj, 'canonical_url', '') or settings.SITE_URL + request.path
    number = request.GET.get('page', '')
    if number.isdigit() and int(number) > 1 and not getattr(obj, 'canonical_url', ''):
        canonical += f'?page={int(number)}'
    crumbs = [('Home', '/')] + (crumbs or [])
    org_id = settings.SITE_URL + '/#organization'
    graph = [{'@type': schema_type, 'name': title, 'description': description, 'url': canonical,
              'isPartOf': {'@id': settings.SITE_URL + '/#website'}, 'inLanguage': 'en'},
             {'@type': 'Organization', '@id': org_id, 'name': company, 'url': settings.SITE_URL + '/'},
             {'@type': 'WebSite', '@id': settings.SITE_URL + '/#website', 'url': settings.SITE_URL + '/', 'name': company,
              'publisher': {'@id': org_id}},
             {'@type': 'BreadcrumbList', 'itemListElement': [
                 {'@type': 'ListItem', 'position': i + 1, 'name': label, 'item': settings.SITE_URL + path}
                 for i, (label, path) in enumerate(crumbs)]}]
    if site and site.logo:
        graph[1]['logo'] = _abs(site.logo.url)
    if schema_type == 'Product' and obj:
        graph[0].update(image=_abs(obj.image_url), category=obj.category.name, brand={'@id': org_id})
        if obj.description: graph[0]['description'] = obj.description
        if obj.model_reference: graph[0].update(model=obj.model_reference, sku=obj.model_reference)
    if schema_type == 'CreativeWork' and obj:
        graph[0].update(image=_abs(obj.image_url), name=obj.title)
    if items:
        graph.append({'@type': 'ItemList', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'url': settings.SITE_URL + item.get_absolute_url(), 'name': getattr(item, 'name', None) or item.title}
            for i, item in enumerate(items)]})
    og_image = getattr(seo, 'og_image', None)
    social = og_image.url if og_image else (obj.image_url if obj is not None and hasattr(obj, 'image_url') else '')
    extra_params = [k for k in request.GET if k != 'page']
    context.update(page_title=title, meta_description=description, canonical=canonical,
                   og_title=getattr(seo, 'og_title', '') or title, og_description=getattr(seo, 'og_description', '') or description,
                   breadcrumbs=crumbs, schema={'@context': 'https://schema.org', '@graph': graph},
                   noindex=(not settings.SITE_INDEXABLE) or bool(extra_params) or bool(getattr(seo, 'noindex', False)) or context.get('noindex', False))
    if social:
        context['social_image'] = _abs(social)
    if pc is not None:
        context['pc'] = pc
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
    request._footer_categories = list(nav_categories())
    pc = page_content('products')
    title = category.name if category else pc.heading
    context = {'listing': pager, 'category': category, 'catalogue_categories': request._footer_categories, 'total_products': public_products().count(),
               'filters': filters, 'q': q, 'selected_category': selected_category, 'sort': sort,
               'query_string': params.urlencode(), 'heading': title}
    return page(request, 'catalogue/products.html', title,
                category.description if category else pc.seo_description,
                context, category, [('Products', '/products/')] + ([(category.name, category.get_absolute_url())] if category else []), 'CollectionPage',
                pc=pc, items=list(pager))


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
    base = public_projects().prefetch_related('gallery')
    sectors = list(base.exclude(application='').order_by('application').values_list('application', flat=True).distinct())
    sector = request.GET.get('sector', '')
    qs = base.filter(application=sector) if sector else base
    qs = qs.order_by('-featured', 'order', 'pk')
    lead = None  # Every reference belongs in the compact, consistently filtered listing.
    pager = Paginator(qs.exclude(pk=lead.pk) if lead else qs, 9).get_page(request.GET.get('page'))
    pc = page_content('projects')
    return page(request, 'catalogue/projects.html', pc.heading, pc.seo_description,
                {'listing': pager, 'lead': lead, 'total': base.count(), 'sectors': sectors, 'sector': sector,
                 'query_string': urlencode({'sector': sector} if sector else {})},
                crumbs=[('Projects', '/projects/')], schema_type='CollectionPage', pc=pc, items=list(pager))


@never_cache
def project_detail(request, slug):
    obj = get_object_or_404(public_projects().prefetch_related('gallery'), slug=slug)
    return page(request, 'catalogue/project.html', obj.title, obj.description,
                {'project': obj, 'related_products': public_products().filter(projects=obj),
                 'more_projects': public_projects().exclude(pk=obj.pk).order_by('-featured', 'order', 'pk')[:3]}, obj,
                [('Projects', '/projects/'), (obj.title, obj.get_absolute_url())], 'CreativeWork')


@never_cache
def solutions(request, slug=None):
    if slug:
        obj = get_object_or_404(Application, published=True, slug=slug)
        return page(request, 'catalogue/solution.html', obj.name + ' solutions', 'Explore ' + obj.name.lower() + ' applications and connected product categories with NCCT. ' + obj.description,
                    {'solution': obj, 'solution_guide':solution_copy(obj.name), 'solution_categories': obj.categories.filter(published=True),
                     'related_products': public_products().filter(applications=obj),
                     'related_projects': public_projects().filter(applications=obj)}, obj,
                    [('Solutions', '/solutions/'), (obj.name, obj.get_absolute_url())])
    applications = list(Application.objects.filter(published=True))
    for application in applications:
        application.editorial = solution_copy(application.name)
    explorer = application_links(applications)
    for item in explorer:
        matched = next((obj for obj in applications if obj.get_absolute_url() == item['solution_url']), None)
        item['guide'] = matched.editorial if matched else None
        item['solution_name'] = matched.name if matched else ''
        item['categories'] = matched.categories.filter(published=True) if matched else []
    pc = page_content('solutions')
    return page(request, 'catalogue/solutions.html', pc.heading, pc.seo_description,
                {'applications': applications, 'application_links':explorer}, crumbs=[('Solutions', '/solutions/')], schema_type='CollectionPage', pc=pc)


@never_cache
def resources(request):
    qs = Resource.objects.filter(published=True).select_related('category')
    types = [(key, label) for key, label in Resource.TYPES if qs.filter(document_type=key).exists()]
    kind = request.GET.get('type', '')
    if kind: qs = qs.filter(document_type=kind)
    q = request.GET.get('q', '').strip()[:200]
    if q: qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
    guides = [g for g in GUIDES if not q or q.casefold() in (' '.join([g['title'],g['intro'],g['group']] + [text for heading,text in g['sections']])).casefold()]
    groups = [(name, [g for g in guides if g['group']==name]) for name in ('Technical guides','Lighting selection','Application knowledge','Insights')]
    pc = page_content('resources')
    return page(request, 'catalogue/resources.html', pc.heading, pc.seo_description,
                {'documents': qs, 'resource_types': types, 'selected_type': kind, 'q':q, 'guide_groups':groups, 'guide_count':len(guides), 'faqs':FAQS}, crumbs=[('Resources', '/resources/')], schema_type='CollectionPage', pc=pc)


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
    if slug == 'about':
        context['about_projects'] = public_projects().exclude(image='', static_image='').order_by('-featured', 'order', 'pk')[:4]
        context['cta'] = page_content('about')
        return page(request, 'catalogue/about.html', obj.title, obj.introduction, context, obj, [(obj.title, obj.get_absolute_url())])
    return page(request, 'catalogue/page.html', obj.title, obj.introduction, context, obj, [(obj.title, obj.get_absolute_url())])


@never_cache
def contact(request):
    pc = page_content('contact')
    return page(request, 'catalogue/contact.html', pc.heading, pc.seo_description, crumbs=[('Contact', '/contact/')], schema_type='ContactPage', pc=pc)


@never_cache
def guide(request, slug):
    article = GUIDE_BY_SLUG.get(slug)
    if article is None:
        raise Http404('Guide unavailable')
    return page(request, 'catalogue/guide.html', article['title'], article['intro'],
                {'guide':article, 'related_guides':[g for g in GUIDES if g['group']==article['group'] and g['slug']!=slug][:3]},
                crumbs=[('Resources','/resources/'),(article['title'],request.path)], schema_type='Article')


def application_detail(request, slug):
    from .application_content import APPLICATION_BY_SLUG
    guidance = APPLICATION_BY_SLUG.get(slug)
    if guidance is None:
        raise Http404
    query = Q()
    for key in guidance['keys']:
        query |= Q(name__icontains=key)
    categories = Category.objects.filter(published=True).filter(query)
    solutions = Application.objects.filter(published=True).filter(query)
    products = public_products().filter(category__in=categories)[:6]
    return page(request, 'catalogue/application.html', guidance['title'] + ' lighting', guidance['intro'],
                {'application': guidance, 'categories': categories, 'solutions': solutions, 'related_products': products},
                crumbs=[('Solutions', '/solutions/'), (guidance['title'], request.path)])
