from django.contrib import admin
from .models import Homepage, Capability, VerifiedMetric

@admin.register(Homepage)
class HomepageAdmin(admin.ModelAdmin):
    exclude = ['privacy_text', 'terms_text', 'cookie_text']
    save_on_top = True
    fieldsets = [
        ('Hero', {'fields': ['hero_heading','hero_copy','hero_caption','image','image_alt','static_image']}),
        ('Introduction', {'fields': ['introduction_heading','introduction']}),
        ('Homepage sections', {'fields': ['show_projects','projects_heading','show_solutions','solutions_heading','show_capabilities','show_products','products_heading','contact_heading']}),
        ('Company & contact', {'fields': ['company_name','logo','footer_description','email','phone','address']}),
        ('Search & verification', {'fields': ['seo_title','seo_description','google_verification','bing_verification']}),
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
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'published', 'order']
    list_editable = ['published', 'order']
    search_fields = ['name', 'description']
    list_filter = ['published']
    prepopulated_fields = {'slug': ['name']}
    filter_horizontal = ['categories']

@admin.register(ContentPage)
class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'published', 'updated_at']
    search_fields = ['title', 'body']
    list_filter = ['published']
    prepopulated_fields = {'slug': ['title']}
    fieldsets = [('Page', {'fields': ['title', 'slug', 'published', 'introduction', 'body']}), ('Search & sharing', {'fields': ['seo_title', 'seo_description', 'canonical_url']})]

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'document_type', 'category', 'published', 'featured', 'order', 'file_size']
    list_editable = ['published', 'featured', 'order']
    list_filter = ['document_type', 'published', 'category']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ['title']}
    filter_horizontal = ['products']
    readonly_fields = ['file_size', 'updated_at']
