from django.test import TestCase, override_settings
from django.core.management import call_command
from core.models import PageContent, Homepage
from core.editorial import GUIDES
from products.models import Product, Category
from projects.models import Project

class EditorialRedesignTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_homepage', verbosity=0)
        call_command('import_ncct_content', verbosity=0)

    def test_all_guides_have_readable_content_and_unknown_guide_404(self):
        for guide in GUIDES:
            response = self.client.get('/resources/guides/' + guide['slug'] + '/')
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, guide['title'])
            self.assertContains(response, guide['sections'][0][1])
        self.assertEqual(self.client.get('/resources/guides/missing/').status_code, 404)

    def test_search_covers_guides_and_retains_document_filter(self):
        response = self.client.get('/resources/?q=driver&type=datasheet')
        self.assertContains(response, 'Product and Driver Compatibility')
        self.assertNotContains(response, 'Designing With Light and Shadow')
        self.assertEqual(response.context['selected_type'], 'datasheet')

    def test_admin_heading_and_intro_remain_authoritative(self):
        PageContent.objects.update_or_create(key='resources', defaults={'heading':'Edited resource heading','intro':'Edited resource introduction'})
        response = self.client.get('/resources/')
        self.assertContains(response, 'Edited resource heading')
        self.assertContains(response, 'Edited resource introduction')
        self.assertEqual(PageContent.objects.get(key='resources').heading, 'Edited resource heading')

    def test_contact_has_one_form_and_same_submission_contract(self):
        response = self.client.get('/contact/')
        html = response.content.decode()
        self.assertEqual(html.count('id="enquiry-form"'), 1)
        self.assertIn('action="/enquiry/"', html)
        self.assertIn('name="token"', html)
        self.assertIn('name="csrfmiddlewaretoken"', html)
        self.assertNotIn('<dialog class="enquiry-drawer"', html)

    def test_category_search_sort_and_page_query_are_retained(self):
        category = Category.objects.filter(published=True).first()
        response = self.client.get('/products/', {'category':category.slug,'sort':'name'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(p.category_id == category.pk for p in response.context['listing']))
        self.assertIn('category='+category.slug, response.context['query_string'])
        self.assertEqual(response.context['sort'], 'name')

    def test_unverified_reference_does_not_publish_client_or_location(self):
        project = Project.objects.filter(published=True).first()
        project.attribution_verified = False
        project.client = 'PRIVATE CLIENT SENTINEL'
        project.location = 'PRIVATE LOCATION SENTINEL'
        project.save()
        response = self.client.get(project.get_absolute_url())
        self.assertContains(response, 'Lighting reference')
        self.assertNotContains(response, 'PRIVATE CLIENT SENTINEL')
        self.assertNotContains(response, 'PRIVATE LOCATION SENTINEL')

    @override_settings(SITE_INDEXABLE=True)
    def test_guides_are_discoverable_in_sitemap(self):
        response = self.client.get('/sitemap.xml')
        for guide in GUIDES:
            self.assertContains(response, '/resources/guides/'+guide['slug']+'/')
