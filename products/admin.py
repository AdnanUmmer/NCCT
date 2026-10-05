from django.contrib import admin
from core.admin_utils import PreviewMixin, InlinePreview, seo_fieldset
from .models import Category, Product, ProductImage, ProductSpecification, ProductFeature


class ImageInline(InlinePreview, admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'preview', 'image_alt', 'caption', 'order']
    readonly_fields = ['preview']
    verbose_name = 'gallery image'
    verbose_name_plural = 'Gallery images (drag-free: set the number in Order)'
    ordering = ['order']


class SpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1


class FeatureInline(admin.TabularInline):
    model = ProductFeature
    extra = 1


@admin.register(Category)
class CategoryAdmin(PreviewMixin, admin.ModelAdmin):
    list_display = ['thumb', 'name', 'product_count', 'status_badge', 'order', 'updated_at']
    list_display_links = ['thumb', 'name']
    list_editable = ['order']
    list_filter = ['published']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']
    prepopulated_fields = {'slug': ['name']}
    readonly_fields = ['preview']
    actions = ['make_published', 'make_unpublished']
    save_on_top = True
    fieldsets = [
        ('Category', {'fields': ['name', 'slug', 'description', 'published', 'order']}),
        ('Image', {'fields': ['image', 'image_alt', 'static_image', 'preview'], 'description': 'Upload a replacement to change the image. Always add alt text describing the image.'}),
        ('Source', {'classes': ['collapse'], 'fields': ['source_url']}),
        seo_fieldset(),
    ]

    @admin.display(description='Products')
    def product_count(self, obj):
        return obj.product_set.count()


@admin.register(Product)
class ProductAdmin(PreviewMixin, admin.ModelAdmin):
    list_display = ['thumb', 'name', 'category', 'model_reference', 'status_badge', 'featured_badge', 'order', 'updated_at']
    list_display_links = ['thumb', 'name']
    list_select_related = ['category']
    list_filter = ['category', 'published', 'featured', 'verified', 'mounting_type', 'ip_rating']
    list_editable = ['order']
    list_per_page = 25
    ordering = ['category__order', 'order', 'name']
    search_fields = ['name', 'model_reference', 'description', 'category__name']
    prepopulated_fields = {'slug': ['name', 'model_reference']}
    date_hierarchy = None
    filter_horizontal = ['applications']
    readonly_fields = ['preview']
    inlines = [ImageInline, SpecificationInline, FeatureInline]
    actions = ['make_published', 'make_unpublished', 'make_featured', 'remove_featured']
    save_on_top = True
    fieldsets = [
        ('1 · Basic information', {'fields': ['name', 'category', 'model_reference']}),
        ('2 · Content', {'fields': ['description', 'full_description', 'applications']}),
        ('3 · Primary image', {'description': 'The main picture shown in listings and at the top of the product page. Add more pictures in the gallery below.', 'fields': ['image', 'image_alt', 'preview', 'static_image']}),
        ('4 · Technical information', {'description': 'Only enter specifications that are confirmed. More rows are in the Specifications and Features sections below.', 'fields': ['mounting_type', 'ip_rating', 'colour_temperature', 'specifications']}),
        ('5 · Publishing', {'fields': ['published', 'featured', 'order', 'verified', 'source_url']}),
        seo_fieldset(slug=True),
    ]
