from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.templatetags.static import static

class HomepageSeedState(models.Model):
    """One-time initialization receipt, committed atomically with starter data."""
    key = models.CharField(max_length=80, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ImageContent(models.Model):
    image = models.ImageField(upload_to='homepage/%Y/%m/', blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp', 'avif'])])
    image_alt = models.CharField(max_length=250)
    static_image = models.CharField(max_length=160, blank=True, help_text='Bundled image basename, without extension.')

    class Meta:
        abstract = True

    @property
    def image_url(self):
        return self.image.url if self.image else static(f'images/{self.static_image}.webp' if self.static_image else 'images/placeholder.svg')

    @property
    def image_small_url(self):
        return self.image.url if self.image else static(f'images/{self.static_image}-800.webp' if self.static_image else 'images/placeholder.svg')

    def clean(self):
        super().clean()
        if self.image and self.image.size > 5 * 1024 * 1024:
            raise ValidationError({'image': 'Upload an optimised image smaller than 5 MB.'})

class Homepage(ImageContent):
    hero_heading = models.CharField(max_length=100, default='Light that\nshapes space.')
    hero_copy = models.CharField(max_length=240, default='Architectural and professional lighting.\nFor the spaces we live, work and move through.')
    hero_caption = models.CharField(max_length=180, default='Architectural lighting · NCCT image library')
    introduction_heading = models.CharField(max_length=100, default='Engineering light.\nElevating spaces.')
    introduction = models.TextField(default='NCCT brings LED lighting into architecture — indoors, outdoors and across decorative, industrial and professional applications. Light that serves a purpose and gives a space its character.')
    email = models.EmailField(default='info@ncctdxb.com')
    phone = models.CharField(max_length=32, default='+971 58 1310300')
    address = models.CharField(max_length=200, default='Office 2202, Ubora Tower, Al Abraj Street, Business Bay, Dubai, UAE')
    privacy_text = models.TextField(blank=True, help_text='Approved privacy notice. Leave blank until supplied.')
    terms_text = models.TextField(blank=True)
    cookie_text = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return 'Homepage & contact settings'

class Capability(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)
    class Meta:
        ordering = ['order', 'pk']
    def __str__(self): return self.title

class VerifiedMetric(models.Model):
    value = models.CharField(max_length=20)
    label = models.CharField(max_length=80)
    source = models.URLField(help_text='Evidence supporting this number.')
    published = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)
    class Meta:
        ordering = ['order', 'pk']
    def __str__(self): return f'{self.value} {self.label}'
