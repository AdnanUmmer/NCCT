from django.contrib import admin
from django.utils.html import format_html
from .models import Enquiry


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'company_name', 'email', 'phone', 'project_type', 'received', 'status_badge']
    list_display_links = ['name', 'company_name']
    list_filter = ['status', 'project_type', 'created_at']
    search_fields = ['name', 'company_name', 'email', 'message']
    date_hierarchy = 'created_at'
    list_per_page = 25
    actions = ['mark_contacted', 'mark_closed', 'mark_new']
    save_on_top = True
    readonly_fields = ['name', 'company_name', 'email_link', 'phone', 'project_type', 'message_text', 'created_at', 'source_page', 'consent', 'consent_text']
    fieldsets = [
        ('Sender', {'fields': ['name', 'company_name', 'email_link', 'phone']}),
        ('Enquiry', {'fields': ['project_type', 'message_text', 'created_at']}),
        ('Follow-up', {'fields': ['status'], 'description': 'Update the status as the team responds. Enquiry details cannot be edited.'}),
        ('Submission details', {'classes': ['collapse'], 'fields': ['source_page', 'consent', 'consent_text']}),
    ]

    @admin.display(description='Received', ordering='created_at')
    def received(self, obj):
        return obj.created_at.strftime('%d %b %Y, %H:%M')

    @admin.display(description='Status', ordering='status')
    def status_badge(self, obj):
        css = {'new': 'badge-new', 'contacted': 'badge-info'}.get(obj.status, 'badge-muted')
        return format_html('<span class="badge {}">{}</span>', css, obj.get_status_display())

    @admin.display(description='Email')
    def email_link(self, obj):
        return format_html('<a href="mailto:{0}">{0}</a>', obj.email)

    @admin.display(description='Message')
    def message_text(self, obj):
        return format_html('<div class="message-box">{}</div>', obj.message or 'No message supplied.')

    @admin.action(description='Mark selected as contacted')
    def mark_contacted(self, request, queryset):
        self.message_user(request, f'{queryset.update(status="contacted")} marked as contacted.')

    @admin.action(description='Mark selected as closed')
    def mark_closed(self, request, queryset):
        self.message_user(request, f'{queryset.update(status="closed")} closed.')

    @admin.action(description='Mark selected as new')
    def mark_new(self, request, queryset):
        self.message_user(request, f'{queryset.update(status="new")} marked as new.')

    def has_add_permission(self, request): return False
