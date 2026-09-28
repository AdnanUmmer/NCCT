from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'location', 'attribution_verified', 'featured', 'order']
    list_filter = ['attribution_verified', 'featured']
    list_editable = ['featured', 'order']
    search_fields = ['title', 'location']
