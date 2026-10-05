from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .admin_utils import PreviewMixin, seo_fieldset
from .models import Homepage, Capability, VerifiedMetric, PageContent

@admin.register(Homepage)
class HomepageAdmin(PreviewMixin, admin.ModelAdmin):
    readonly_fields = ['preview']
    exclude = ['privacy_text', 'terms_text', 'cookie_text']
    save_on_top = True
    fieldsets = [
        ('Hero', {'fields': ['hero_eyebrow','hero_heading','hero_copy','hero_caption','hero_cta_text','hero_cta_link','hero_secondary_text','hero_secondary_link','image','image_alt','static_image','preview'], 'description': 'Buttons: leave text blank to hide a button. Links may be a page path such as /projects/ or a full https:// address.'}),
        ('Introduction', {'fields': ['introduction_heading','introduction']}),
        ('Homepage sections', {'fields': ['show_projects','projects_heading','show_solutions','solutions_heading','show_capabilities','show_products','products_heading','contact_heading']}),
        ('Company & contact', {'fields': ['company_name','logo','footer_description','email','phone','address']}),
        ('Home page search & sharing (SEO)', {'fields': ['seo_title','seo_description','og_image']}),
        ('Analytics & webmaster tools', {'classes': ['collapse'], 'description': 'Paste only tokens supplied by Google or Bing. Analytics loads only once the site is live and indexable.', 'fields': ['ga4_measurement_id','google_verification','bing_verification']}),
    ]
    def has_add_permission(self, request): return not Homepage.objects.exists()
    def has_delete_permission(self, request, obj=None): return False

@admin.register(Capability)
class CapabilityAdmin(admin.ModelAdmin):
    list_display = ['title', 'order']
    list_editable = ['order']

@admin.register(VerifiedMetric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ['value', 'label', 'source', 'published', 'order']
    list_editable = ['published', 'order']


from .models import Application, ContentPage, Resource

@admin.register(Application)
class ApplicationAdmin(PreviewMixin, admin.ModelAdmin):
    list_display = ['thumb', 'name', 'status_badge', 'order', 'updated_at']
    list_display_links = ['thumb', 'name']
    ordering = ['order', 'name']
    readonly_fields = ['preview']
    actions = ['make_published', 'make_unpublished']
    save_on_top = True
    list_editable = ['order']
    search_fields = ['name', 'description']
    list_filter = ['published']
    prepopulated_fields = {'slug': ['name']}
    filter_horizontal = ['categories']
    fieldsets = [('Solution', {'fields': ['name', 'slug', 'description', 'categories', 'published', 'order']}), ('Image', {'fields': ['image', 'image_alt', 'static_image', 'preview']}), ('Source', {'classes': ['collapse'], 'fields': ['source_url']}), seo_fieldset()]

@admin.register(ContentPage)
class PageAdmin(PreviewMixin, admin.ModelAdmin):
    save_on_top = True
    list_display = ['title', 'slug', 'status_badge', 'updated_at']
    search_fields = ['title', 'body']
    list_filter = ['published']
    prepopulated_fields = {'slug': ['title']}
    fieldsets = [('Page', {'fields': ['title', 'slug', 'published', 'introduction', 'body']}), ('Hero image', {'fields': ['image', 'image_alt'], 'description': 'Used on the About page. Leave blank to use the default NCCT interior image.'}), seo_fieldset()]

@admin.register(Resource)
class ResourceAdmin(PreviewMixin, admin.ModelAdmin):
    actions = ['make_published', 'make_unpublished', 'make_featured', 'remove_featured']
    ordering = ['order', 'title']
    save_on_top = True
    list_display = ['cover_thumb', 'title', 'document_type', 'category', 'file_label', 'status_badge', 'featured_badge', 'order', 'size_kb', 'download_link']
    list_display_links = ['cover_thumb', 'title']
    list_editable = ['order']
    list_filter = ['document_type', 'published', 'category']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ['title']}
    filter_horizontal = ['products']
    readonly_fields = ['file_size', 'updated_at', 'download_link', 'cover_preview']
    fieldsets = [
        ('Document', {'fields': ['title', 'slug', 'document_type', 'category', 'description', 'language']}),
        ('File', {'fields': ['file', 'bundled_file', 'file_size', 'download_link'], 'description': 'Upload a PDF to add or replace the download. The old file is not served once replaced.'}),
        ('Cover / thumbnail', {'fields': ['cover', 'cover_alt', 'cover_preview']}),
        ('Publication', {'fields': ['published', 'featured', 'order', 'products', 'source_url', 'updated_at']}),
        seo_fieldset(),
    ]

    @admin.display(description='Cover preview')
    def cover_preview(self, obj):
        return format_html('<img src="{}" alt="" style="max-width:220px;max-height:160px">', obj.cover.url) if obj and obj.cover else '—'

    @admin.display(description='Cover')
    def cover_thumb(self, obj):
        if obj.cover:
            return format_html('<img src="{}" alt="" class="list-thumb" width="54" height="72">', obj.cover.url)
        return format_html('<span class="doc-ico">PDF</span>')

    @admin.display(description='File')
    def file_label(self, obj):
        name = obj.file.name.rsplit('/', 1)[-1] if obj.file else obj.bundled_file
        return name or '—'

    @admin.display(description='Size')
    def size_kb(self, obj):
        return f'{obj.file_size // 1024} KB' if obj.file_size else '—'

    @admin.display(description='Download')
    def download_link(self, obj):
        if not obj.pk:
            return '—'
        return format_html('<a href="{}" target="_blank" rel="noopener">Test download</a>', reverse('resource-download', args=[obj.slug]))


@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    """Editable headings, intros and call-to-action text for the main public pages."""
    list_display = ['page_name', 'heading', 'updated_at']
    list_display_links = ['page_name', 'heading']
    search_fields = ['heading', 'intro']
    ordering = ['key']
    save_on_top = True
    readonly_fields = ['key']
    fieldsets = [
        ('Page header', {'fields': ['key', 'eyebrow', 'heading', 'intro', 'notice'], 'description': 'Wrap words in *asterisks* to show them in the italic accent style, e.g. Projects *in light.*'}),
        ('Call-to-action band', {'fields': ['cta_eyebrow', 'cta_heading', 'cta_text', 'cta_link'], 'description': 'Leave the link blank to open the enquiry form. Clear the heading to hide the band.'}),
        ('Search & social sharing (SEO)', {'classes': ['collapse'], 'fields': ['seo_title', 'seo_description', 'og_title', 'og_description', 'og_image', 'noindex']}),
    ]

    @admin.display(description='Page', ordering='key')
    def page_name(self, obj):
        return obj.get_key_display()

    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False

from . import admin_site  # noqa: F401,E402
