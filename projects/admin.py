from django.contrib import admin
from .models import Project, ProjectImage

class ImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'location', 'attribution_verified', 'published', 'featured', 'order']
    list_filter = ['attribution_verified', 'published', 'featured']
    list_editable = ['featured', 'order']
    search_fields = ['title', 'location']

    prepopulated_fields = {'slug': ['title']}
    filter_horizontal = ['products', 'applications']
    inlines = [ImageInline]
