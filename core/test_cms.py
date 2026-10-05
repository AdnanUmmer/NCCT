import json
import tempfile
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from products.models import Product
from projects.models import Project
from .models import Homepage, PageContent, Resource
from .test_admin import STORAGES, png


@override_settings(STORAGES=STORAGES, MEDIA_ROOT=tempfile.mkdtemp(), SITE_INDEXABLE=True, SECURE_SSL_REDIRECT=False)
class CmsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_homepage', verbosity=0)
        call_command('import_ncct_content', verbosity=0)
        cls.user = get_user_model().objects.create_superuser('qa-cms', 'qa@example.com', 'x' * 20)

    def test_dashboard_and_page_content_admin(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('admin:index'))
        self.assertContains(response, 'Quick actions')
        self.assertContains(response, 'Recent enquiries')
        self.assertContains(response, 'class="sidebar"')
        row = PageContent.objects.get(key='projects')
        self.assertEqual(self.client.get(reverse('admin:core_pagecontent_change', args=[row.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse('admin:core_pagecontent_add')).status_code, 403)

    def test_page_content_edit_reflects_on_frontend(self):
        PageContent.objects.filter(key='contact').update(heading='Talk to our team', seo_title='Custom contact title', seo_description='Custom contact description for search engines that is long enough.')
        html = self.client.get('/contact/').content.decode()
        self.assertIn('Talk to our team', html)
        self.assertIn('<title>Custom contact title | ', html)
        self.assertIn('property="og:title"', html)
        self.assertIn('rel="canonical" href="https://ncctdxb.com/contact/"', html)

    def test_homepage_cta_and_heading(self):
        Homepage.objects.update(hero_heading='A brand new heading', hero_cta_text='See our work', hero_cta_link='/projects/', hero_secondary_text='')
        html = self.client.get('/').content.decode()
        self.assertIn('A brand new heading', html)
        self.assertIn('See our work', html)
        self.assertNotIn('Discover solutions', html)

    def test_noindex_and_sitemap_exclusion(self):
        product = Product.objects.filter(published=True).first()
        url = product.get_absolute_url()
        self.assertIn(url, self.client.get('/sitemap.xml').content.decode())
        Product.objects.filter(pk=product.pk).update(noindex=True)
        self.assertNotIn(url, self.client.get('/sitemap.xml').content.decode())
        self.assertIn('noindex', self.client.get(url).content.decode())
        self.assertNotIn('/admin/', self.client.get('/sitemap.xml').content.decode())

    def test_filtered_pages_noindex_and_canonical_is_clean(self):
        html = self.client.get('/products/?q=light').content.decode()
        self.assertIn('noindex', html)
        self.assertIn('rel="canonical" href="https://ncctdxb.com/products/"', html)

    def test_product_schema_and_unpublish(self):
        product = Product.objects.filter(published=True).first()
        html = self.client.get(product.get_absolute_url()).content.decode()
        blocks = [json.loads(b.split('</script>')[0]) for b in html.split('application/ld+json">')[1:]]
        self.assertTrue(any('Product' in json.dumps(b) for b in blocks))
        self.assertNotIn('aggregateRating', html)
        Product.objects.filter(pk=product.pk).update(published=False)
        self.assertEqual(self.client.get(product.get_absolute_url()).status_code, 404)

    def test_resource_cover_upload_and_download(self):
        self.client.force_login(self.user)
        resource = Resource.objects.filter(published=True).first()
        resource.cover.save('cover.png', png(), save=False)
        resource.cover_alt = 'Datasheet cover'
        resource.save()
        self.assertContains(self.client.get('/resources/'), 'Datasheet cover')
        self.assertEqual(self.client.get(reverse('resource-download', args=[resource.slug])).status_code, 200)
        resource.cover.delete(save=True)
        self.assertEqual(self.client.get('/resources/').status_code, 200)

    def test_project_hidden_when_unpublished(self):
        project = Project.objects.filter(published=True).first()
        Project.objects.filter(pk=project.pk).update(published=False)
        self.assertEqual(self.client.get(project.get_absolute_url()).status_code, 404)
        self.assertNotContains(self.client.get('/projects/'), project.get_absolute_url())
