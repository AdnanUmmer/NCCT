from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from core.models import Homepage, HomepageSeedState, Capability, VerifiedMetric
from products.models import Category, Product
from projects.models import Project


class HomepageSeedingTests(TestCase):
    def seed(self):
        call_command('seed_homepage', stdout=StringIO())

    def snapshot(self):
        return {model.__name__: list(model.objects.order_by('pk').values()) for model in
                (Homepage, Category, Project, Product, Capability, VerifiedMetric, HomepageSeedState)}

    def test_empty_database_and_repeat(self):
        self.seed()
        self.assertEqual(Homepage.objects.count(), 1)
        self.assertEqual(Category.objects.count(), 5)
        self.assertEqual(Project.objects.filter(featured=True).count(), 3)
        self.assertEqual(Product.objects.filter(featured=True, verified=True).count(), 3)
        self.assertEqual(Capability.objects.count(), 4)
        self.assertEqual(VerifiedMetric.objects.count(), 0)
        self.assertEqual(Homepage.objects.get().static_image, 'single-light-v2')
        before = self.snapshot()
        self.seed()
        self.assertEqual(before, self.snapshot())

    def test_admin_renames_uploads_flags_and_deletions_are_preserved(self):
        self.seed()
        Homepage.objects.update(hero_heading='Admin headline', image='homepage/custom.webp')
        Category.objects.update(name='Renamed category', description='Admin description')
        Project.objects.update(title='Renamed project', featured=False, image='homepage/project.webp')
        Product.objects.update(name='Renamed product', verified=False, featured=False)
        Capability.objects.first().delete()
        Capability.objects.update(title='Renamed capability')
        before = self.snapshot()
        self.seed()
        self.assertEqual(before, self.snapshot())

    def test_pre_receipt_admin_content_is_preserved(self):
        self.seed()
        HomepageSeedState.objects.all().delete()
        Category.objects.update(name='Custom category')
        Project.objects.update(title='Custom project', featured=False)
        Product.objects.update(name='Custom product', verified=False)
        Capability.objects.update(title='Custom capability')
        before = self.snapshot()
        self.seed()
        after = self.snapshot()
        before.pop('HomepageSeedState'); after.pop('HomepageSeedState')
        self.assertEqual(before, after)

    def test_failure_rolls_back_receipt_and_content(self):
        with patch('core.management.commands.seed_homepage.Project.objects.get_or_create', side_effect=RuntimeError('test failure')):
            with self.assertRaises(RuntimeError): self.seed()
        self.assertFalse(HomepageSeedState.objects.exists())
        self.assertFalse(Homepage.objects.exists())
        self.assertFalse(Category.objects.exists())
        self.seed()
        self.assertEqual(Product.objects.count(), 3)

    def test_ambiguous_existing_categories_fail_without_writing(self):
        Category.objects.create(name='Admin category', image_alt='Admin image')
        before = self.snapshot()
        with self.assertRaises(CommandError): self.seed()
        self.assertEqual(before, self.snapshot())
