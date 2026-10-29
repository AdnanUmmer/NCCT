from django.db import migrations


ALT = 'Architectural luminaires against dark stone with warm integrated lighting'
CAPTION = 'Architectural lighting, considered in context'


def use_new_default_hero(apps, schema_editor):
    Homepage = apps.get_model('core', 'Homepage')
    Homepage.objects.filter(
        image='',
        static_image='single-light-v2',
    ).update(
        static_image='hero',
        image_alt=ALT,
        hero_caption=CAPTION,
    )


def restore_old_default_hero(apps, schema_editor):
    Homepage = apps.get_model('core', 'Homepage')
    Homepage.objects.filter(
        image='',
        static_image='hero',
        image_alt=ALT,
        hero_caption=CAPTION,
    ).update(
        static_image='single-light-v2',
        image_alt='Concept image of a single bronze pendant casting warm light onto stone',
        hero_caption='Single light study / Generated concept',
    )


class Migration(migrations.Migration):
    dependencies = [('core', '0007_seed_page_content')]

    operations = [
        migrations.RunPython(use_new_default_hero, restore_old_default_hero),
    ]
