from django.db import migrations


def remove_about_subheading(apps, schema_editor):
    ContentPage = apps.get_model('core', 'ContentPage')
    ContentPage.objects.filter(
        slug='about',
        introduction='Illuminating Spaces. Inspiring Experiences.',
    ).update(introduction='')


class Migration(migrations.Migration):
    dependencies = [('core', '0009_about_images_and_copy')]

    operations = [
        migrations.RunPython(remove_about_subheading, migrations.RunPython.noop),
    ]
