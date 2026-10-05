from django.db import migrations


def seed(apps, schema_editor):
    from core.page_defaults import PAGE_DEFAULTS
    PageContent = apps.get_model('core', 'PageContent')
    for key, values in PAGE_DEFAULTS.items():
        PageContent.objects.get_or_create(key=key, defaults=values)


class Migration(migrations.Migration):
    dependencies = [('core', '0006_seo_social_and_page_content')]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
