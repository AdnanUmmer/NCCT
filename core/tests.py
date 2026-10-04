import json
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from .models import Homepage, VerifiedMetric
from products.models import Product

class HomepageTests(TestCase):
    @classmethod
    def setUpTestData(cls): call_command('seed_homepage',verbosity=0)

    def test_page_and_structured_data(self):
        response=self.client.get('/')
        self.assertEqual(response.status_code,200)
        text=response.content.decode()
        self.assertIn('Light that<br>shapes space.',text)
        self.assertIn('application/ld+json',text)
        schema=json.loads(text.split('<script type="application/ld+json">')[1].split('</script>')[0])
        self.assertEqual(schema['@graph'][0]['name'],'NCCT')
        self.assertIn('await confirmation',text)

    def test_seed_is_idempotent_and_keeps_edits(self):
        content=Homepage.objects.get();content.hero_heading='Edited heading';content.save()
        call_command('seed_homepage',verbosity=0)
        self.assertEqual(Homepage.objects.count(),1);self.assertEqual(Product.objects.count(),3)
        self.assertContains(self.client.get('/'),'Edited heading')

    def test_unverified_products_and_unpublished_metrics_hidden(self):
        Product.objects.update(verified=False)
        VerifiedMetric.objects.create(value='999',label='Unverified claim',source='https://example.test')
        response=self.client.get('/')
        self.assertNotContains(response,'Ceiling lighting');self.assertNotContains(response,'Unverified claim')

    @override_settings(DEBUG=False,SECURE_SSL_REDIRECT=False)
    def test_custom_404(self):
        for path in ['/missing/']:
            response=self.client.get(path);self.assertEqual(response.status_code,404);self.assertContains(response,'off course',status_code=404)

    def test_admin_content_pages(self):
        user=get_user_model().objects.create_superuser('admin','admin@example.test','temporary-test-password')
        self.client.force_login(user)
        for path in ['core/homepage','core/capability','core/verifiedmetric','products/category','products/product','projects/project']:
            self.assertEqual(self.client.get('/admin/'+path+'/').status_code,200)

    def test_schema_escapes_admin_text(self):
        content=Homepage.objects.get();content.address='</script><script>alert(1)</script>';content.save()
        response=self.client.get('/');self.assertNotContains(response,'</script><script>alert(1)</script>')
