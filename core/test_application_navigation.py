from django.test import TestCase
from django.core.management import call_command
from django.urls import reverse
from core.application_content import APPLICATION_PAGES
from products.models import Product

class ApplicationNavigationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_homepage', verbosity=0)
        call_command('import_ncct_content', verbosity=0)

    def test_seven_distinct_destinations_and_related_content(self):
        home = self.client.get('/')
        paths = [reverse('application-detail', args=[a['slug']]) for a in APPLICATION_PAGES]
        self.assertEqual(len(set(paths)), 7)
        for a, path in zip(APPLICATION_PAGES, paths):
            self.assertContains(home, path)
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['application']['slug'], a['slug'])
            self.assertContains(response, a['intro'])
            self.assertTrue(response.context['categories'].exists())
            self.assertTrue(response.context['solutions'].exists())
            self.assertTrue(response.context['related_products'])
        self.assertEqual(self.client.get('/applications/not-real/').status_code, 404)

    def test_uploaded_replacement_is_authoritative(self):
        p = Product.objects.first()
        p.static_image = 'outside_p3'
        p.image = 'products/custom-replacement.webp'
        self.assertEqual(p.image_url, p.image.url)

    def test_chevrons_are_decorative_vectors(self):
        response = self.client.get('/')
        self.assertNotContains(response, '\u2197')
        self.assertContains(response, 'class="link-chevron"')
        self.assertContains(response, 'stroke="currentColor"')
