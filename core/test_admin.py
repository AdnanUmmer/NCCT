import tempfile
from io import BytesIO
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image
from products.models import Category, Product, ProductImage
from projects.models import Project, ProjectImage
from .models import ContentPage, Resource

STORAGES = {'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
            'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}}


def png(name='x.png'):
    buffer = BytesIO()
    Image.new('RGB', (40, 30), 'orange').save(buffer, 'PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), 'image/png')


@override_settings(STORAGES=STORAGES, MEDIA_ROOT=tempfile.mkdtemp())
class AdminCrudTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_homepage', verbosity=0)
        call_command('import_ncct_content', verbosity=0)
        cls.user = get_user_model().objects.create_superuser('qa-admin', 'qa@example.com', 'x' * 20)

    def setUp(self):
        self.client.force_login(self.user)

    def test_changelists_and_add_forms_render(self):
        for model in ('products.category', 'products.product', 'projects.project', 'core.resource',
                      'core.contentpage', 'core.application', 'core.homepage', 'core.capability'):
            app, name = model.split('.')
            self.assertEqual(self.client.get(reverse(f'admin:{app}_{name}_changelist')).status_code, 200, model)
        for model in ('products.product', 'projects.project', 'core.resource', 'products.category'):
            app, name = model.split('.')
            self.assertEqual(self.client.get(reverse(f'admin:{app}_{name}_add')).status_code, 200, model)
        self.assertEqual(self.client.get(reverse('admin:products_product_changelist'), {'q': 'LED'}).status_code, 200)

    def test_product_image_upload_change_delete(self):
        category = Category.objects.first()
        data = {'name': 'QA Lamp', 'slug': 'qa-lamp', 'category': category.pk, 'verified': 'on', 'published': 'on', 'order': 1,
                'image': png(), 'image_alt': 'QA lamp',
                'gallery-TOTAL_FORMS': 0, 'gallery-INITIAL_FORMS': 0, 'gallery-MIN_NUM_FORMS': 0, 'gallery-MAX_NUM_FORMS': 1000,
                'specification_rows-TOTAL_FORMS': 0, 'specification_rows-INITIAL_FORMS': 0, 'specification_rows-MIN_NUM_FORMS': 0, 'specification_rows-MAX_NUM_FORMS': 1000,
                'features-TOTAL_FORMS': 0, 'features-INITIAL_FORMS': 0, 'features-MIN_NUM_FORMS': 0, 'features-MAX_NUM_FORMS': 1000}
        response = self.client.post(reverse('admin:products_product_add'), data)
        self.assertEqual(response.status_code, 302, getattr(response, 'context', None) and response.context['adminform'].form.errors)
        product = Product.objects.get(slug='qa-lamp')
        self.assertTrue(product.image.name)
        self.assertEqual(self.client.get(product.get_absolute_url()).status_code, 200)
        data.update(name='QA Lamp renamed', image=png('y.png'))
        self.assertEqual(self.client.post(reverse('admin:products_product_change', args=[product.pk]), data).status_code, 302)
        product.refresh_from_db(); self.assertEqual(product.name, 'QA Lamp renamed')
        self.assertEqual(self.client.post(reverse('admin:products_product_delete', args=[product.pk]), {'post': 'yes'}).status_code, 302)
        self.assertFalse(Product.objects.filter(pk=product.pk).exists())

    def test_project_crud_and_actions(self):
        project = Project.objects.create(title='QA Project', application='Interior', image_alt='x', published=True, featured=False)
        ProjectImage.objects.create(project=project, static_image='homepg-1', image_alt='x', caption='Caption')
        self.assertContains(self.client.get(project.get_absolute_url()), 'Caption')
        self.client.post(reverse('admin:projects_project_changelist'), {'action': 'make_unpublished', '_selected_action': [project.pk]})
        project.refresh_from_db(); self.assertFalse(project.published)
        self.assertEqual(self.client.get(project.get_absolute_url()).status_code, 404)
        self.client.post(reverse('admin:projects_project_changelist'), {'action': 'make_published', '_selected_action': [project.pk]})
        self.assertEqual(self.client.get(project.get_absolute_url()).status_code, 200)
        self.assertEqual(self.client.post(reverse('admin:projects_project_delete', args=[project.pk]), {'post': 'yes'}).status_code, 302)

    def test_resource_upload_and_download(self):
        pdf = SimpleUploadedFile('brochure.pdf', b'%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n', 'application/pdf')
        response = self.client.post(reverse('admin:core_resource_add'), {'title': 'QA Brochure', 'slug': 'qa-brochure', 'document_type': 'brochure',
                                    'language': 'English', 'published': 'on', 'order': 1, 'file': pdf})
        self.assertEqual(response.status_code, 302)
        download = self.client.get('/resources/qa-brochure/download/')
        self.assertEqual(download.status_code, 200)
        self.assertEqual(download['Content-Type'], 'application/pdf')
        for resource in Resource.objects.filter(bundled_file__endswith='.pdf'):
            self.assertEqual(self.client.get(reverse('resource-download', args=[resource.slug])).status_code, 200)

    def test_about_image_editable(self):
        page = ContentPage.objects.get(slug='about')
        page.image = png('about.png'); page.image_alt = 'Hero'; page.save()
        self.assertContains(self.client.get('/about/'), 'alt="Hero"')
