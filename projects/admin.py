from django.contrib import admin
from core.admin_utils import PreviewMixin, InlinePreview, seo_fieldset
from .models import Project, ProjectImage


class ImageInline(InlinePreview, admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ['image', 'preview', 'image_alt', 'caption', 'order']
    readonly_fields = ['preview']
    ordering = ['order']
    verbose_name = 'gallery image'
    verbose_name_plural = 'Project gallery (use Order to arrange; tick Delete to remove)'


@admin.register(Project)
class ProjectAdmin(PreviewMixin, admin.ModelAdmin):
    list_display = ['thumb', 'title', 'application', 'location', 'status_badge', 'featured_badge', 'order', 'updated_at']
    list_display_links = ['thumb', 'title']
    list_filter = ['published', 'featured', 'attribution_verified', 'application']
    list_editable = ['order']
    ordering = ['order', 'title']
    search_fields = ['title', 'location', 'client', 'description']
    prepopulated_fields = {'slug': ['title']}
    filter_horizontal = ['products', 'applications']
    readonly_fields = ['preview']
    inlines = [ImageInline]
    actions = ['make_published', 'make_unpublished', 'make_featured', 'remove_featured']
    save_on_top = True
    fieldsets = [
        ('1 · Project', {'fields': ['title', 'application', 'location', 'description', 'scope']}),
        ('2 · Cover image', {'fields': ['image', 'image_alt', 'static_image', 'preview'], 'description': 'Add further photos in the Gallery section below.'}),
        ('3 · Related products & solutions', {'fields': ['products', 'applications']}),
        ('4 · Project facts (only when confirmed)', {'classes': ['collapse'], 'fields': ['client', 'year', 'source_url']}),
        ('5 · Publishing', {'fields': ['published', 'featured', 'order', 'attribution_verified'], 'description': 'Tick "attribution verified" only when this is a genuine delivered NCCT project; otherwise it is shown as a lighting reference.'}),
        seo_fieldset(slug=True),
    ]
