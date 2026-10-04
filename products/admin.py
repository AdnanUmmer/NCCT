from django.contrib import admin
from .models import Category, Product, ProductImage, ProductSpecification, ProductFeature

class ImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
class SpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 0
class FeatureInline(admin.TabularInline):
    model = ProductFeature
    extra = 0

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'published', 'order']
    list_editable = ['published', 'order']
    search_fields = ['name']
    prepopulated_fields = {'slug': ['name']}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'model_reference', 'category', 'verified', 'published', 'featured', 'order']
    list_select_related = ['category']
    list_filter = ['category', 'verified', 'published', 'featured']
    list_editable = ['published', 'featured', 'order']
    search_fields = ['name', 'model_reference', 'description']
    prepopulated_fields = {'slug': ['name', 'model_reference']}
    filter_horizontal = ['applications']
    inlines = [ImageInline, SpecificationInline, FeatureInline]
    fieldsets = [('Identity & publication', {'fields': ['name','slug','model_reference','category','source_url','verified','published','featured','order']}), ('Content & image', {'fields': ['description','full_description','image','image_alt','static_image']}), ('Technical information', {'fields': ['mounting_type','ip_rating','colour_temperature','specifications','applications']}), ('Search & sharing', {'fields': ['seo_title','seo_description','canonical_url']})]
