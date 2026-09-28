from django.db import models
from core.models import ImageContent

class Category(ImageContent):
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=240)
    source_url = models.URLField()
    order = models.PositiveSmallIntegerField(default=0)
    class Meta:
        ordering = ['order', 'pk']
        verbose_name_plural = 'categories'
    def __str__(self): return self.name

class Product(ImageContent):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    description = models.TextField(blank=True)
    specifications = models.CharField(max_length=180, blank=True, help_text='Verified specifications only.')
    source_url = models.URLField(blank=True)
    verified = models.BooleanField(default=False)
    featured = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)
    class Meta:
        ordering = ['order', 'pk']
    def __str__(self): return self.name
