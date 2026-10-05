from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.text import slugify


class Publishable(models.Model):
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    published = models.BooleanField(default=True, db_index=True)
    seo_title = models.CharField(max_length=100, blank=True)
    seo_description = models.CharField(max_length=300, blank=True)
    canonical_url = models.URLField(blank=True, help_text='Optional canonical override. Normally leave blank.')
    og_title = models.CharField('Social share title', max_length=100, blank=True, help_text='Optional. Defaults to the search title.')
    og_description = models.CharField('Social share description', max_length=300, blank=True, help_text='Optional. Defaults to the search description.')
    og_image = models.ImageField('Social share image', upload_to='social/%Y/%m/', blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])], help_text='Optional. 1200x630 px works best. Defaults to the main image.')
    noindex = models.BooleanField('Hide from search engines', default=False, help_text='Tick only for pages that should not appear in Google. Also removes the page from the sitemap.')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(getattr(self, 'name', None) or getattr(self, 'title', 'content'))[:150] or 'content'
            self.slug = base
            i = 2
            while type(self).objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f'{base}-{i}'
                i += 1
        super().save(*args, **kwargs)
