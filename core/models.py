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

    company_name = models.CharField(max_length=100, default='NCCT')
    footer_description = models.CharField(max_length=250, default='Architectural & professional lighting. Dubai, United Arab Emirates.')
    logo = models.ImageField(upload_to='company/', blank=True, validators=[FileExtensionValidator(['png', 'webp', 'jpg'])])
    seo_title = models.CharField(max_length=100, default='NCCT — Architectural & Professional Lighting')
    seo_description = models.CharField(max_length=300, default='Explore NCCT indoor, outdoor, decorative, industrial and professional lighting. Based in Business Bay, Dubai.')
    google_verification = models.CharField(max_length=150, blank=True)
    bing_verification = models.CharField(max_length=150, blank=True)
    projects_heading = models.CharField(max_length=100, default='Spaces, brought to light.')
    products_heading = models.CharField(max_length=100, default='The detail makes the difference.')
    solutions_heading = models.CharField(max_length=100, default='The right light. For every setting.')
    contact_heading = models.CharField(max_length=120, default="Let's bring your space to light.")
    show_projects = models.BooleanField(default=True)
    show_products = models.BooleanField(default=True)
    show_solutions = models.BooleanField(default=True)
    show_capabilities = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.logo and self.logo.size > 5 * 1024 * 1024:
            raise ValidationError({'logo': 'Use a logo smaller than 5 MB.'})

    def __str__(self):
        return 'Homepage & contact settings'

class Capability(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)
    class Meta:
        ordering = ['order', 'pk']
        verbose_name_plural = 'capabilities'
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


from .content import Publishable
from .validators import validate_pdf
from django.urls import reverse

class Application(ImageContent, Publishable):
    name = models.CharField(max_length=120)
    description = models.TextField()
    source_url = models.URLField(blank=True)
    categories = models.ManyToManyField('products.Category', blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    class Meta:
        ordering = ['order', 'pk']
    def __str__(self): return self.name
    def get_absolute_url(self): return reverse('solution-detail', args=[self.slug])

class ContentPage(Publishable):
    title = models.CharField(max_length=150)
    introduction = models.TextField(blank=True)
    body = models.TextField(blank=True)
    class Meta:
        ordering = ['title']
    def __str__(self): return self.title
    def get_absolute_url(self): return reverse('content-page', args=[self.slug])

class Resource(Publishable):
    TYPES = [('datasheet', 'Technical datasheet'), ('catalogue', 'Catalogue'), ('brochure', 'Brochure'), ('installation', 'Installation guide'), ('certificate', 'Certificate'), ('company', 'Company profile')]
    title = models.CharField(max_length=150)
    document_type = models.CharField(max_length=20, choices=TYPES, default='datasheet')
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='documents/%Y/%m/', blank=True, validators=[validate_pdf])
    bundled_file = models.CharField(max_length=180, blank=True, help_text='Bundled PDF filename under static/documents; leave blank for uploads.')
    file_size = models.PositiveIntegerField(default=0, editable=False)
    language = models.CharField(max_length=40, default='English')
    source_url = models.URLField(blank=True)
    category = models.ForeignKey('products.Category', null=True, blank=True, on_delete=models.SET_NULL)
    products = models.ManyToManyField('products.Product', blank=True, related_name='documents')
    featured = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)
    class Meta:
        ordering = ['order', 'title']
    def __str__(self): return self.title
    def get_absolute_url(self): return reverse('resource-download', args=[self.slug])
    def clean(self):
        super().clean()
        from pathlib import Path
        from django.conf import settings
        if not self.file and not self.bundled_file:
            raise ValidationError('Upload a PDF or select an existing bundled PDF.')
        if self.bundled_file:
            if Path(self.bundled_file).name != self.bundled_file or not self.bundled_file.endswith('.pdf'):
                raise ValidationError({'bundled_file': 'Use a PDF basename without directories.'})
            if not (settings.BASE_DIR / 'static/documents' / self.bundled_file).is_file():
                raise ValidationError({'bundled_file': 'Bundled PDF does not exist.'})
    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
        elif self.bundled_file:
            from django.conf import settings
            path = settings.BASE_DIR / 'static/documents' / self.bundled_file
            if path.is_file(): self.file_size = path.stat().st_size
        super().save(*args, **kwargs)
