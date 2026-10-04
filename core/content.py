from django.db import models
from django.utils.text import slugify


class Publishable(models.Model):
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    published = models.BooleanField(default=True, db_index=True)
    seo_title = models.CharField(max_length=100, blank=True)
    seo_description = models.CharField(max_length=300, blank=True)
    canonical_url = models.URLField(blank=True, help_text='Optional canonical override. Normally leave blank.')
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
