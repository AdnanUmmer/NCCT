from django.contrib import admin
from .models import Enquiry

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ['company_name','name','project_type','created_at','status']
    list_filter = ['status','project_type','created_at']
    search_fields = ['name','company_name','email']
    list_editable = ['status']
    readonly_fields = ['name','company_name','email','phone','project_type','message','consent','consent_text','created_at','source_page','submission_id','fingerprint']
    def has_add_permission(self, request): return False
