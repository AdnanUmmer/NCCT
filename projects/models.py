from django.db import models
from core.models import ImageContent

class Project(ImageContent):
    title = models.CharField(max_length=150)
    location = models.CharField(max_length=100, blank=True)
    application = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    source_url = models.URLField(blank=True)
    attribution_verified = models.BooleanField(default=False, help_text='Confirm NCCT delivery and image rights before publishing as a completed project.')
    featured = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)
    class Meta:
        ordering = ['order', 'pk']
    def __str__(self): return self.title
