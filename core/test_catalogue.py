import json
import tempfile
from io import BytesIO
from pathlib import Path
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from PIL import Image
from .models import Application, ContentPage, Resource, Homepage
from .validators import validate_pdf
from products.models import Product, Category
from projects.models import Project


@override_settings(STORAGES={'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'}, 'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}})
class CatalogueTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_homepage', verbosity=0)
        call_command('import_ncct_content', verbosity=0)

    def test_routes_and_unique_metadata(self):
        paths = ['/', '/products/', '/projects/', '/solutions/', '/resources/', '/about/', '/contact/', '/privacy/', '/terms/', '/cookies/']
        paths += [x.get_absolute_url() for Model in (Product, Category, Application) for x in Model.objects.all()]
        titles = []
        for path in paths:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            html = response.content.decode()
            self.assertEqual(html.count('<h1'), 1, path)
            self.assertIn('rel="canonical"', html)
            self.assertIn('og:image', html)
            titles.append(html.split('<title>')[1].split('</title>')[0])
            for block in html.split('<script type="application/ld+json">')[1:]:
                json.loads(block.split('</script>')[0])
        self.assertEqual(len(titles), len(set(titles)))

    def test_import_preserves_renames_deletions_and_admin_edits(self):
        obj = Product.objects.get(model_reference='SPJ105')
        obj.name = 'Administrator title'; obj.model_reference = 'Edited'; obj.published = False; obj.save()
        Resource.objects.first().delete()
        Application.objects.first().delete()
        before = (Product.objects.count(), Resource.objects.count(), Application.objects.count())
        call_command('import_ncct_content', verbosity=0)
        self.assertEqual(before, (Product.objects.count(), Resource.objects.count(), Application.objects.count()))
        obj.refresh_from_db(); self.assertEqual(obj.name, 'Administrator title'); self.assertFalse(obj.published)

    def test_filters_combine_retain_and_clear(self):
        response = self.client.get('/products/', {'q':'SPJ105','ip_rating':'IP66','mounting_type':'Bracket and spike','sort':'name'})
        self.assertEqual(response.context['listing'].paginator.count, 1)
        self.assertContains(response, 'value="SPJ105"')
        response = self.client.get('/products/', {'q':'SPJ105','ip_rating':'IP68'})
        self.assertContains(response, 'No matching products')
        self.assertEqual(self.client.get('/products/').context['listing'].paginator.count, 8)

    def test_pagination_invalid_input(self):
        for value in ['abc', '-4', '999']:
            self.assertEqual(self.client.get('/products/', {'page':value}).status_code, 200)

    def test_drafts_and_unverified_projects_not_public(self):
        product = Product.objects.get(model_reference='SPJ105')
        product.published=False; product.save()
        self.assertEqual(self.client.get(product.get_absolute_url()).status_code,404)
        category = Category.objects.get(pk=product.category_id)
        category.published=False; category.save()
        self.assertEqual(self.client.get(category.get_absolute_url()).status_code,404)
        for project in Project.objects.all():
            self.assertEqual(self.client.get(project.get_absolute_url()).status_code,404)
        self.assertNotContains(self.client.get('/projects/'), 'The architecture of atmosphere')

    def test_verified_project_detail_and_related_product(self):
        project = Project.objects.first(); project.attribution_verified=True; project.description='Verified test project'; project.save()
        project.products.add(Product.objects.first())
        response = self.client.get(project.get_absolute_url())
        self.assertContains(response, 'Verified test project')
        self.assertContains(response, 'Products in this project')
        project.published=False; project.save()
        self.assertEqual(self.client.get(project.get_absolute_url()).status_code,404)

    def test_all_downloads_and_unpublishing(self):
        self.assertEqual(Resource.objects.count(), 5)
        for resource in Resource.objects.all():
            response = self.client.get(resource.get_absolute_url())
            self.assertEqual(response.status_code,200)
            self.assertEqual(response['Content-Type'],'application/pdf')
            self.assertTrue(b''.join(response.streaming_content).startswith(b'%PDF-'))
            self.assertIn('attachment;',response['Content-Disposition'])
            resource.published=False; resource.save()
            self.assertEqual(self.client.get(resource.get_absolute_url()).status_code,404)

    @override_settings(SITE_INDEXABLE=True, SITE_URL='https://design.theadvoxy.com')
    def test_sitemap_canonical_and_robots(self):
        product = Product.objects.first()
        response = self.client.get('/sitemap.xml')
        self.assertContains(response, 'https://design.theadvoxy.com'+product.get_absolute_url())
        product.published=False; product.save()
        self.assertNotContains(self.client.get('/sitemap.xml'), product.get_absolute_url())
        self.assertContains(self.client.get('/robots.txt'),'Sitemap: https://design.theadvoxy.com/sitemap.xml')
        self.assertContains(self.client.get('/products/?q=test'), 'noindex, follow')
        self.assertNotContains(self.client.get('/products/'),'noindex, follow')

    def test_legacy_redirects(self):
        for old,new in [('/en/index.html','/'),('/en/do-pobrania-2/products.html','/resources/'),('/en/contact-2/index.html','/contact/')]:
            response = self.client.get(old)
            self.assertEqual(response.status_code,301)
            self.assertEqual(response['Location'],new)

    def test_pdf_validation(self):
        for upload in [SimpleUploadedFile('evil.pdf', b'<html>not a pdf</html>', content_type='application/pdf'), SimpleUploadedFile('bad.html',b'%PDF-1.7')]:
            with self.assertRaises(ValidationError): validate_pdf(upload)
        validate_pdf(SimpleUploadedFile('valid.pdf',b'%PDF-1.7\n',content_type='application/pdf'))

    def test_admin_pages_and_content_crud(self):
        user = get_user_model().objects.create_superuser('qa-admin', 'qa@example.test', 'temporary-test-only-password')
        self.client.force_login(user)
        for path in ['core/contentpage', 'core/application', 'core/resource', 'products/product', 'projects/project', 'core/homepage']:
            self.assertEqual(self.client.get('/admin/'+path+'/').status_code,200)
        response=self.client.post('/admin/core/contentpage/add/', {'title':'Admin page', 'slug':'admin-page','introduction':'Test introduction','body':'Test body','published':'on','_save':'Save'})
        self.assertEqual(response.status_code,302)
        obj=ContentPage.objects.get(slug='admin-page')
        self.assertContains(self.client.get(obj.get_absolute_url()),'Test body')
        response=self.client.post(f'/admin/core/contentpage/{obj.pk}/change/', {'title':'Updated page','slug':'admin-page','introduction':'Edited introduction','body':'Edited body','_save':'Save'})
        self.assertEqual(response.status_code,302)
        self.assertEqual(self.client.get(obj.get_absolute_url()).status_code,404)
        self.client.post(f'/admin/core/contentpage/{obj.pk}/delete/', {'post':'yes'})
        self.assertFalse(ContentPage.objects.filter(pk=obj.pk).exists())

    def test_image_upload_and_pdf_replacement(self):
        with tempfile.TemporaryDirectory(dir=settings.BASE_DIR) as folder, override_settings(MEDIA_ROOT=folder):
            buffer=BytesIO(); Image.new('RGB',(20,20),'blue').save(buffer,format='PNG')
            obj=Product.objects.first(); obj.image=SimpleUploadedFile('sample.png',buffer.getvalue(),content_type='image/png');obj.full_clean();obj.save()
            self.assertTrue(Path(obj.image.path).is_file())
            obj.image.close()
            self.assertContains(self.client.get(obj.get_absolute_url()), obj.image.url)
            doc=Resource.objects.first();doc.file=SimpleUploadedFile('replace.pdf',b'%PDF-1.7\n',content_type='application/pdf');doc.full_clean();doc.save()
            response=self.client.get(doc.get_absolute_url());self.assertEqual(b''.join(response.streaming_content),b'%PDF-1.7\n');response.close();doc.file.close()

    def test_query_count_does_not_grow_per_product(self):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext
        with CaptureQueriesContext(connection) as queries:
            self.client.get('/products/')
        self.assertLessEqual(len(queries), 10)

    def test_500_does_not_query_database(self):
        from .views import server_error
        from django.test import RequestFactory
        with self.assertNumQueries(0):
            response=server_error(RequestFactory().get('/'))
        self.assertEqual(response.status_code,500)


    @override_settings(ADMIN_LOGIN_RATE_LIMIT=2)
    def test_admin_login_rate_limit(self):
        self.client.post('/admin/login/', {'username':'absent','password':'invalid'})
        self.client.post('/admin/login/', {'username':'absent','password':'invalid'})
        response=self.client.post('/admin/login/', {'username':'absent','password':'invalid'})
        self.assertEqual(response.status_code,429)
        self.assertEqual(response['Retry-After'],'600')
