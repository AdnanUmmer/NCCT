from django.core.management import call_command
from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import reverse

from core.models import Resource
from products.models import Category
from projects.models import Project


class AboutResourcesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_homepage', verbosity=0)
        call_command('import_ncct_content', verbosity=0)

    def test_about_selects_four_public_images_and_preserves_attribution(self):
        Project.objects.create(title='Hidden project', slug='hidden', published=False,
                               static_image='architecture', order=0)
        Project.objects.create(title='No project image', slug='no-image', published=True, order=0)
        response = self.client.get('/about/')
        selected = list(response.context['about_projects'])
        self.assertEqual(len(selected), 4)
        self.assertTrue(all(p.published and (p.image or p.static_image) for p in selected))
        self.assertContains(response, 'class="about-project-slide"', count=4)
        self.assertNotContains(response, 'Hidden project')
        self.assertNotContains(response, 'No project image')
        self.assertNotContains(response, 'Nine collections.')
        for project in selected:
            self.assertContains(response, project.get_absolute_url())
            self.assertContains(response, project.image_small_url)
        self.assertContains(response, 'View Reference', count=4)
        selected[0].attribution_verified = True
        selected[0].save()
        response = self.client.get('/about/')
        self.assertContains(response, 'Explore Project', count=1)
        self.assertContains(response, 'View Reference', count=3)
        self.assertContains(response, f'href="{reverse("projects")}"')
        self.assertEqual(self.client.get(reverse('projects')).status_code, 200)

    def test_about_slider_is_separate_from_the_homepage_gallery(self):
        response = self.client.get('/about/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sections/about_project_slider.html')
        self.assertContains(response, 'js/about-project-slider.js')
        self.assertContains(response, 'css/about-project-slider.css')
        self.assertContains(response, 'SELECTED PROJECTS &amp; REFERENCES')
        self.assertContains(response, 'Explore selected lighting references and discover how illumination shapes architectural spaces.')
        self.assertNotContains(response, 'js/lighting-gallery.')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sections/moments_gallery.html')
        self.assertContains(response, 'js/lighting-gallery.')
        self.assertContains(response, 'css/lighting-gallery.')
        response = self.client.get('/')
        self.assertContains(response, 'Lighting for Every Moment')
        self.assertContains(response, 'class="moment-card"', count=Category.objects.filter(published=True).count())

    def test_shared_template_has_instance_scoped_ids(self):
        items = Category.objects.filter(published=True)[:2]
        first = render_to_string('sections/moments_gallery.html', {'items': items, 'gallery_id': 'first'})
        second = render_to_string('sections/moments_gallery.html', {'items': items, 'gallery_id': 'second'})
        import re
        first_ids = set(re.findall(r'\bid="([^"]+)"', first))
        second_ids = set(re.findall(r'\bid="([^"]+)"', second))
        self.assertFalse(first_ids & second_ids)

    def test_resources_put_real_downloads_before_guides(self):
        response = self.client.get('/resources/')
        html = response.content.decode()
        self.assertContains(response, 'href="#documents">Browse Downloads')
        self.assertLess(html.index('class="document-list"'), html.index('id="technical-guides"'))
        for document in Resource.objects.filter(published=True):
            self.assertContains(response, document.get_absolute_url())
            download = self.client.get(document.get_absolute_url())
            self.assertEqual(download.status_code, 200)
            self.assertEqual(download['Content-Type'], 'application/pdf')
            self.assertIn('attachment;', download['Content-Disposition'])
            self.assertTrue(b''.join(download.streaming_content).startswith(b'%PDF-'))
            download.close()

    def test_empty_download_results_keep_enquiry_and_guides(self):
        Resource.objects.update(published=False)
        response = self.client.get('/resources/')
        self.assertContains(response, 'No documents match this selection.')
        self.assertContains(response, 'Request a datasheet')
        self.assertContains(response, 'id="technical-guides"')
        self.assertNotContains(response, 'class="document-row"')

    def test_enquiry_cta_preserves_custom_and_modal_destinations(self):
        for link in ('', '/contact/?source=about'):
            html = render_to_string('catalogue/cta_band.html', {'cta': {
                'cta_heading': 'Talk to NCCT', 'cta_text': 'Discuss Your Project', 'cta_link': link}})
            self.assertIn('>Enquire</a>', html)
            self.assertIn(f'href="{link or "#enquiry"}"', html)
            self.assertEqual('data-enquire' in html, not bool(link))
