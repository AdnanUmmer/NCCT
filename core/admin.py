from django.contrib import admin
from .models import Homepage, Capability, VerifiedMetric

@admin.register(Homepage)
class HomepageAdmin(admin.ModelAdmin):
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
