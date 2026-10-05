from django.contrib import admin
from django.utils.html import format_html


class PreviewMixin:
    """Thumbnail columns/fields and bulk publish actions for admin classes."""

    @admin.display(description='Image')
    def thumb(self, obj):
        url = getattr(obj, 'image_small_url', '') or getattr(obj, 'image_url', '')
        if not url:
            return '—'
        return format_html('<img src="{}" alt="" class="list-thumb" width="72" height="54">', url)

    @admin.display(description='Preview')
    def preview(self, obj):
        url = getattr(obj, 'image_url', '') if obj and obj.pk else ''
        if not url:
            return 'Save to see a preview.'
        return format_html('<img src="{}" alt="" class="field-preview-img">', url)

    @admin.display(description='Status', ordering='published')
    def status_badge(self, obj):
        return format_html('<span class="badge {}">{}</span>', 'badge-ok' if obj.published else 'badge-muted', 'Published' if obj.published else 'Draft')

    @admin.display(description='Featured', ordering='featured', boolean=False)
    def featured_badge(self, obj):
        return format_html('<span class="badge badge-gold">Featured</span>') if getattr(obj, 'featured', False) else format_html('<span class="muted">—</span>')

    @admin.action(description='Publish selected')
    def make_published(self, request, queryset):
        self.message_user(request, f'{queryset.update(published=True)} published.')

    @admin.action(description='Unpublish selected')
    def make_unpublished(self, request, queryset):
        self.message_user(request, f'{queryset.update(published=False)} unpublished.')

    @admin.action(description='Mark as featured')
    def make_featured(self, request, queryset):
        self.message_user(request, f'{queryset.update(featured=True)} featured.')

    @admin.action(description='Remove from featured')
    def remove_featured(self, request, queryset):
        self.message_user(request, f'{queryset.update(featured=False)} updated.')


class InlinePreview:
    @admin.display(description='File')
    def filename(self, obj):
        return obj.image.name.rsplit('/', 1)[-1] if obj and obj.pk and obj.image else '—'

    @admin.display(description='Preview')
    def preview(self, obj):
        url = getattr(obj, 'image_small_url', '') if obj and obj.pk else ''
        return format_html('<img src="{}" alt="" class="inline-thumb">', url) if url else '—'


SEO_HELP = ('Leave blank to use sensible defaults built from the content above. Meta titles read best at 50-60 characters, '
            'descriptions at 120-158. Only tick "Hide from search engines" for pages that must not appear in Google.')


def seo_fieldset(canonical=True, slug=False):
    fields = (['slug'] if slug else []) + ['seo_title', 'seo_description', 'og_title', 'og_description', 'og_image', 'noindex']
    if canonical:
        fields.append('canonical_url')
    return ('Search & social sharing (SEO)', {'classes': ['collapse'], 'description': SEO_HELP, 'fields': fields})
