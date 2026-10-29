from django.db import migrations


ABOUT_INTRODUCTION = 'Illuminating Spaces. Inspiring Experiences.'
ABOUT_BODY = (
    'At NCCT, we believe lighting is more than illumination — it is an essential element of architecture that shapes spaces, '
    'enhances experiences, and brings environments to life. With a focus on quality, innovation, and contemporary design, '
    'we aim to deliver lighting solutions that combine functionality with lasting visual appeal.\n\n'
    'Our approach is rooted in understanding how light interacts with architecture and the people who experience each space. '
    'From sophisticated interiors and commercial environments to outdoor landscapes and public spaces, we focus on lighting '
    'that balances performance, efficiency, and aesthetics.\n\n'
    'Every project has its own identity and purpose. Through thoughtful design and attention to detail, we strive to create '
    'lighting experiences that not only illuminate spaces but elevate the way they are seen and experienced.'
)

CATEGORY_IMAGES = {
    'industrial-lighting-4': ('industrial', 'Modern industrial lighting in a high-bay warehouse'),
    'outdoor-lighting-2': ('outside', 'Exterior path and landscape illuminated with warm architectural lighting'),
    'professional-lighting-5': ('professional', 'Professional studio lighting equipment in a production space'),
    'emergency-lighting': ('emergency', 'Emergency exit signage and lighting in a stairwell'),
}

PROJECT_IMAGES = {
    'the-architecture-of-atmosphere-1': (
        'architecture',
        'Warm architectural interior with sculptural lighting and illuminated landscape',
    ),
    'a-path-quietly-defined-2': ('street', 'Illuminated city street and skyline at night'),
    'after-the-sun-goes-down-3': ('sundown', 'Garden terraces illuminated after sunset'),
}


def update_existing_content(apps, schema_editor):
    ContentPage = apps.get_model('core', 'ContentPage')
    ContentPage.objects.filter(slug='about').update(
        title='About NCCT',
        introduction=ABOUT_INTRODUCTION,
        body=ABOUT_BODY,
    )

    for model_name in ('Category', 'Application'):
        Model = apps.get_model('products' if model_name == 'Category' else 'core', model_name)
        for slug, (image, alt) in CATEGORY_IMAGES.items():
            Model.objects.filter(slug=slug, image='').update(static_image=image, image_alt=alt)

    Project = apps.get_model('projects', 'Project')
    for slug, (image, alt) in PROJECT_IMAGES.items():
        Project.objects.filter(slug=slug, image='').update(static_image=image, image_alt=alt)


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0008_homepage_hero_image'),
        ('products', '0004_seo_social_and_page_content'),
        ('projects', '0004_seo_social_and_page_content'),
    ]

    operations = [
        migrations.RunPython(update_existing_content, migrations.RunPython.noop),
    ]
