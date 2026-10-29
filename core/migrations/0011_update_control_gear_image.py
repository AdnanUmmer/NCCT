from django.db import migrations


def update_control_gear_image(apps, schema_editor):
    Category = apps.get_model('products', 'Category')
    Application = apps.get_model('core', 'Application')

    for model in (Category, Application):
        model.objects.filter(slug='control-gear', image='').update(
            static_image='control',
            image_alt='Lighting control gear and smart lighting equipment',
        )


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0010_remove_about_subheading'),
        ('products', '0004_seo_social_and_page_content'),
    ]

    operations = [
        migrations.RunPython(update_control_gear_image, migrations.RunPython.noop),
    ]
