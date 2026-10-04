from django.db import models

PROJECT_TYPES = [(v, v) for v in ['Commercial', 'Hospitality', 'Residential', 'Retail', 'Infrastructure', 'Industrial', 'Government/Public Sector', 'Other']]

class Enquiry(models.Model):
    name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=32)
    project_type = models.CharField(max_length=30, choices=PROJECT_TYPES, blank=True)
    message = models.TextField(max_length=4000, blank=True)
    consent = models.BooleanField()
    consent_text = models.CharField(max_length=160, default='I agree to be contacted regarding this enquiry.')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    status = models.CharField(max_length=12, choices=[('new','New'), ('contacted','Contacted'), ('closed','Closed')], default='new')
    source_page = models.CharField(max_length=100, default='/')
    submission_id = models.UUIDField(unique=True, editable=False)
    fingerprint = models.CharField(max_length=64, unique=True, editable=False)
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'enquiries'
    def __str__(self): return f'{self.company_name} · {self.name}'

class RateWindow(models.Model):
    key = models.CharField(max_length=64, unique=True)
    count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
