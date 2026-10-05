from django.db import models
from core.models import ImageContent
from core.content import Publishable
from django.urls import reverse

class Category(ImageContent, Publishable):
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=240)
    source_url = models.URLField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    class Meta:
        ordering = ['order', 'pk']
        verbose_name_plural = 'categories'
    def get_absolute_url(self): return reverse('product-category', args=[self.slug])
    def __str__(self): return self.name

class Product(ImageContent, Publishable):
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

    model_reference = models.CharField(max_length=100, blank=True)
    full_description = models.TextField(blank=True)
    mounting_type = models.CharField(max_length=100, blank=True)
    ip_rating = models.CharField(max_length=30, blank=True)
    colour_temperature = models.CharField(max_length=50, blank=True)
    applications = models.ManyToManyField('core.Application', blank=True, related_name='products')
    def get_absolute_url(self): return reverse('product-detail', args=[self.category.slug, self.slug])

class ProductImage(ImageContent):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery')
    caption = models.CharField(max_length=160, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    class Meta:
        ordering = ['order', 'pk']

class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specification_rows')
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=250)
    order = models.PositiveSmallIntegerField(default=0)
    class Meta:
        ordering = ['order', 'pk']
        constraints = [models.UniqueConstraint(fields=['product', 'label'], name='unique_product_spec_label')]

class ProductFeature(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='features')
    text = models.CharField(max_length=250)
    order = models.PositiveSmallIntegerField(default=0)
    class Meta:
        ordering = ['order', 'pk']
