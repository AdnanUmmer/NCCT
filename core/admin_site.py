"""Dashboard data and grouped navigation for the NCCT admin."""
from django.contrib import admin
from django.urls import reverse

GROUPS = [
    ('Website content', 'bi-layout', ['core.homepage', 'core.pagecontent', 'core.contentpage', 'core.capability', 'core.verifiedmetric']),
    ('Product catalogue', 'bi-box', ['products.category', 'products.product', 'core.application']),
    ('Projects', 'bi-building', ['projects.project']),
    ('Resources & downloads', 'bi-file', ['core.resource']),
    ('Enquiries', 'bi-mail', ['enquiries.enquiry']),
    ('Accounts & access', 'bi-key', ['auth.user', 'auth.group']),
]
_original_get_app_list = admin.AdminSite.get_app_list
_original_index = admin.AdminSite.index


def _grouped(site, request):
    flat = {}
    for app in _original_get_app_list(site, request):
        for model in app['models']:
            flat[f"{app['app_label']}.{model['object_name'].lower()}"] = model
    groups, used = [], set()
    for name, _icon, keys in GROUPS:
        models = [flat[k] for k in keys if k in flat]
        used.update(k for k in keys if k in flat)
        if models:
            groups.append({'name': name, 'app_label': name.lower().split()[0], 'app_url': '', 'has_module_perms': True, 'models': models})
    extra = [m for k, m in flat.items() if k not in used]
    if extra:
        groups.append({'name': 'Other', 'app_label': 'other', 'app_url': '', 'has_module_perms': True, 'models': extra})
    return groups


def get_app_list(self, request, app_label=None):
    groups = _grouped(self, request)
    if app_label:
        return [g for g in groups if g['app_label'] == app_label]
    return groups


def index(self, request, extra_context=None):
    from core.models import Resource
    from enquiries.models import Enquiry
    from products.models import Category, Product
    from projects.models import Project
    u = lambda name, qs='': reverse(name) + qs
    stats = [
        ('Total products', Product.objects.count(), u('admin:products_product_changelist'), 'box'),
        ('Published products', Product.objects.filter(published=True).count(), u('admin:products_product_changelist', '?published__exact=1'), 'box'),
        ('Categories', Category.objects.count(), u('admin:products_category_changelist'), 'content'),
        ('Projects', Project.objects.count(), u('admin:projects_project_changelist'), 'building'),
        ('Brochures & resources', Resource.objects.count(), u('admin:core_resource_changelist'), 'file'),
        ('New enquiries', Enquiry.objects.filter(status='new').count(), u('admin:enquiries_enquiry_changelist', '?status__exact=new'), 'mail'),
    ]
    quick = [('Add product', reverse('admin:products_product_add'), 'plus'), ('Add project', reverse('admin:projects_project_add'), 'plus'),
             ('Upload brochure', reverse('admin:core_resource_add'), 'upload'), ('Edit homepage', reverse('admin:core_homepage_changelist'), 'content')]
    drafts = [(label, n, url) for label, n, url in (
        ('unpublished products', Product.objects.filter(published=False).count(), u('admin:products_product_changelist', '?published__exact=0')),
        ('unpublished projects', Project.objects.filter(published=False).count(), u('admin:projects_project_changelist', '?published__exact=0'))) if n]
    context = {
        'stats': stats, 'quick': quick, 'drafts': drafts,
        'recent_enquiries': Enquiry.objects.order_by('-created_at')[:6],
        'recent_products': Product.objects.select_related('category').order_by('-updated_at')[:6],
        'recent_projects': Project.objects.order_by('-updated_at')[:6],
        'recent_resources': Resource.objects.order_by('-updated_at')[:6],
        **(extra_context or {})}
    return _original_index(self, request, context)


admin.AdminSite.get_app_list = get_app_list
admin.AdminSite.index = index
