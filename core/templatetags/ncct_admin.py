from django import template
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

ICONS = {
    'dashboard': '<rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/><rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/>',
    'content': '<path d="M4 4h16v16H4z"/><path d="M4 9h16M9 9v11"/>',
    'box': '<path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="m3 8 9 5 9-5M12 13v8"/>',
    'building': '<path d="M4 21V5l8-2v18M12 8h8v13M8 8h.01M8 12h.01M8 16h.01M16 12h.01M16 16h.01M2 21h20"/>',
    'file': '<path d="M14 3H6a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
    'mail': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    'search': '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    'settings': '<circle cx="12" cy="12" r="3"/><path d="M19 12a7 7 0 0 0-.1-1.2l2-1.6-2-3.4-2.4 1a7 7 0 0 0-2-1.2L14 3h-4l-.4 2.6a7 7 0 0 0-2 1.2l-2.4-1-2 3.4 2 1.6a7 7 0 0 0 0 2.4l-2 1.6 2 3.4 2.4-1a7 7 0 0 0 2 1.2L10 21h4l.4-2.6a7 7 0 0 0 2-1.2l2.4 1 2-3.4-2-1.6c.1-.4.2-.8.2-1.2z"/>',
    'external': '<path d="M14 4h6v6M20 4 10 14M18 14v6H4V6h6"/>',
    'menu': '<path d="M4 6h16M4 12h16M4 18h16"/>',
    'chevron': '<path d="m6 9 6 6 6-6"/>',
    'panel': '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M9 4v16"/>',
    'plus': '<path d="M12 5v14M5 12h14"/>',
    'user': '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/>',
    'close': '<path d="M6 6l12 12M18 6 6 18"/>',
    'upload': '<path d="M12 16V4M7 9l5-5 5 5M4 20h16"/>',
    'image': '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="2"/><path d="m21 16-5-5-9 9"/>',
}


@register.simple_tag
def icon(name, size=18):
    return format_html('<svg class="ico" width="{0}" height="{0}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{1}</svg>', size, mark_safe(ICONS.get(name, '')))


def _url(name, *args):
    try:
        return reverse(name, args=args)
    except Exception:
        return ''


def _singleton(model_path, name):
    from django.apps import apps
    model = apps.get_model(model_path)
    obj = model.objects.first()
    return _url(f'admin:{name}_change', obj.pk) if obj else _url(f'admin:{name}_changelist')


def _page(key):
    from core.models import PageContent
    row = PageContent.objects.filter(key=key).first()
    return _url('admin:core_pagecontent_change', row.pk) if row else _url('admin:core_pagecontent_changelist')


def _about():
    from core.models import ContentPage
    row = ContentPage.objects.filter(slug='about').first()
    return _url('admin:core_contentpage_change', row.pk) if row else _url('admin:core_contentpage_changelist')


@register.simple_tag(takes_context=True)
def admin_nav(context):
    request, user = context['request'], context['request'].user
    path = request.path

    def item(label, url, perm, match=None, new_tab=False):
        if not url or not user.has_perm(perm):
            return None
        return {'label': label, 'url': url, 'new_tab': new_tab, 'match': match or url}

    def v(app, model): return f'{app}.view_{model}'
    def a(app, model): return f'{app}.add_{model}'
    groups = [
        ('Website content', 'content', [
            item('Homepage', _singleton('core.Homepage', 'core_homepage'), v('core', 'homepage'), '/admin/core/homepage/'),
            item('About page', _about(), v('core', 'contentpage'), '/admin/core/contentpage/'),
            item('Contact page', _page('contact'), v('core', 'pagecontent')),
            item('Other pages & legal', _url('admin:core_contentpage_changelist'), v('core', 'contentpage'), '/admin/core/contentpage/'),
            item('Capabilities & metrics', _url('admin:core_capability_changelist'), v('core', 'capability'), '/admin/core/capability/'),
        ]),
        ('Products', 'box', [
            item('All products', _url('admin:products_product_changelist'), v('products', 'product'), '/admin/products/product/'),
            item('Categories', _url('admin:products_category_changelist'), v('products', 'category'), '/admin/products/category/'),
            item('Solutions / applications', _url('admin:core_application_changelist'), v('core', 'application'), '/admin/core/application/'),
            item('Add product', _url('admin:products_product_add'), a('products', 'product'), '/admin/products/product/add/'),
        ]),
        ('Projects', 'building', [
            item('All projects', _url('admin:projects_project_changelist'), v('projects', 'project'), '/admin/projects/project/'),
            item('Add project', _url('admin:projects_project_add'), a('projects', 'project'), '/admin/projects/project/add/'),
        ]),
        ('Resources', 'file', [
            item('Brochures & catalogues', _url('admin:core_resource_changelist'), v('core', 'resource'), '/admin/core/resource/'),
            item('Add resource', _url('admin:core_resource_add'), a('core', 'resource'), '/admin/core/resource/add/'),
        ]),
        ('Enquiries', 'mail', [
            item('All enquiries', _url('admin:enquiries_enquiry_changelist'), v('enquiries', 'enquiry'), '/admin/enquiries/enquiry/'),
        ]),
        ('SEO', 'search', [
            item('Page text & SEO', _url('admin:core_pagecontent_changelist'), v('core', 'pagecontent'), '/admin/core/pagecontent/'),
            item('Sitemap', '/sitemap.xml', 'core.view_pagecontent', '/sitemap.xml', True),
            item('robots.txt', '/robots.txt', 'core.view_pagecontent', '/robots.txt', True),
        ]),
        ('Settings', 'settings', [
            item('Company & analytics', _singleton('core.Homepage', 'core_homepage'), v('core', 'homepage'), '/admin/core/homepage/'),
            item('Users', _url('admin:auth_user_changelist'), v('auth', 'user'), '/admin/auth/user/'),
            item('Groups & roles', _url('admin:auth_group_changelist'), v('auth', 'group'), '/admin/auth/group/'),
        ]),
    ]
    result = []
    best = None
    for name, ico, items in groups:
        items = [i for i in items if i]
        if not items:
            continue
        result.append({'name': name, 'icon': ico, 'items': items, 'open': False})
    # the single most specific matching item is active
    for g in result:
        for i in g['items']:
            i['active'] = False
            if path.startswith(i['match']) and not i['new_tab'] and (best is None or len(i['match']) > len(best[1]['match'])):
                best = (g, i)
    if best:
        best[1]['active'] = True
        best[0]['open'] = True
    return {'groups': result, 'dashboard_active': path.rstrip('/') == '/admin'}
