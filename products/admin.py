from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    list_editable = ['order']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'verified', 'featured', 'order']
    list_filter = ['category', 'verified', 'featured']
    list_editable = ['featured', 'order']
    search_fields = ['name']
