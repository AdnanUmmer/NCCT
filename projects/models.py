from django.db import models
from core.models import ImageContent
from core.content import Publishable
from django.urls import reverse

class Project(ImageContent, Publishable):
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

    client = models.CharField(max_length=150, blank=True, help_text='Only publicly verified client names.')
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    scope = models.TextField(blank=True)
    products = models.ManyToManyField('products.Product', blank=True, related_name='projects')
    applications = models.ManyToManyField('core.Application', blank=True, related_name='projects')
    def get_absolute_url(self): return reverse('project-detail', args=[self.slug])

class ProjectImage(ImageContent):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='gallery')
    caption = models.CharField(max_length=160, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    class Meta:
        ordering = ['order', 'pk']
