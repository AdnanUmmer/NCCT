"""Reviewed source import. No network requests and no updates to existing content."""
from django.core.management.base import BaseCommand
from urllib.parse import quote
from django.db import transaction
from core.models import Homepage, HomepageSeedState, ContentPage, Application, Resource
from products.models import Category, Product, ProductSpecification

SOURCE = 'https://ncctdxb.com/en/do-pobrania-2/products.html'
PRODUCTS = [
    ('Bollard luminaire', 'LB170-600', 'zoomled-bl1', 'Jumeirah J 1/Zoomled BL1.pdf', '20 W', 'IP66', 'Base mounted',
     'A bollard luminaire for pathways and landscape settings.', [('Housing', 'Aluminium'), ('Finish', 'Black'), ('Diffuser', 'Transparent polycarbonate'), ('CRI', '80+'), ('Delivered lumens', '1020 lm'), ('Beam angle', '360°')]),
    ('Inground luminaire', 'SL2161CE-1', 'zoomled-el8-el2', 'Jumeirah J 1/Zoomled EL8_EL2.pdf', '10 W', 'IP68', 'Recessed box',
     'A recessed inground luminaire with a stainless steel trim and a choice of beam distributions.', [('Dimensions', 'Ø135 × H139 mm'), ('Housing', 'Die-cast aluminium with stainless steel trim'), ('Impact resistance', 'IK10')]),
    ('Floor marker luminaire', 'LUP290', 'zoomled-el12a', 'Jumeirah J 1/Zoomled EL12A.pdf', '5 W', 'IP67', 'Recessed box',
     'A floor marker for ground-level lighting, with sector-based light distribution.', [('Dimensions', 'Ø150 × H61 mm'), ('Housing', 'Powder-coated aluminium'), ('Finish', 'Black RAL9011'), ('Impact resistance', 'IK10'), ('Delivered lumens', '230 lm'), ('Beam angle', '120° (two windows)')]),
    ('Spot luminaire', 'SPJ105', 'zoomled-l6-l10', 'Mamzar M 1/Zoomled L6_L10.pdf', '20 W', 'IP66', 'Bracket and spike',
     'An adjustable outdoor spotlight with bracket and spike mounting options.', [('Housing', 'Die-cast aluminium'), ('Finish', 'Black'), ('Diffuser', '4 mm tempered glass'), ('CRI', '80+'), ('Delivered lumens', '1680 lm'), ('Beam angles', '10° / 20° / 45° / 60° / 90° / 120°')]),
    ('Wall recessed luminaire', 'SL2101-A', 'zoomled-l15', 'Mamzar M 1/Zoomled L15.pdf', '5 W', 'IP67', 'Recessed box',
     'A wall recessed luminaire identified in the NCCT-linked Zoomled datasheet.', [('Dimensions', 'Ø75 × H88 mm'), ('Housing', 'Die-cast aluminium with stainless steel trim'), ('Impact resistance', 'IK10'), ('Beam angles', '25° / 120°')]),
]


class Command(BaseCommand):
    help = 'Import reviewed NCCT catalogue and page content once; preserve all later admin changes.'

    @transaction.atomic
    def handle(self, *args, **options):
        _, created = HomepageSeedState.objects.get_or_create(key='catalogue-v1')
        if not created:
            self.stdout.write('Catalogue already initialized; no records changed.')
            return
        outdoor = Category.objects.filter(source_url='https://ncctdxb.com/en/Real/Outdoor_lights.html').first()
        if outdoor is None:
            outdoor, _ = Category.objects.get_or_create(slug='outdoor-lighting', defaults={
                'name': 'Outdoor lighting', 'description': 'Lighting for exterior settings.',
                'source_url': 'https://ncctdxb.com/en/Real/Outdoor_lights.html',
                'static_image': 'homepg-2', 'image_alt': 'Illuminated landscape steps'})
        for category in Category.objects.filter(published=True):
            app, new = Application.objects.get_or_create(slug=category.slug, defaults={
                'name': category.name, 'description': category.description, 'source_url': category.source_url,
                'static_image': category.static_image, 'image_alt': category.image_alt, 'order': category.order})
            if new: app.categories.add(category)
        for order, (name, model, image, source, power, ip, mounting, description, specs) in enumerate(PRODUCTS, 10):
            obj = Product.objects.filter(model_reference=model).first()
            if obj is None:
                obj = Product.objects.create(name=name, model_reference=model, slug=image,
                    category=outdoor, description=description, static_image=image,
                    image_alt=f'{model} {name.lower()}', source_url=SOURCE,
                    verified=True, published=True, featured=False, order=order,
                    mounting_type=mounting, ip_rating=ip, colour_temperature='3000 K')
                application = Application.objects.filter(slug=outdoor.slug).first()
                if application: obj.applications.add(application)
                for i, (label, value) in enumerate([('Power', power), ('Ingress protection', ip), ('Colour temperature', '3000 K'), ('Supply', 'AC 220 V'), ('Control', 'On/off')] + specs):
                    ProductSpecification.objects.create(product=obj, label=label, value=value, order=i)
            doc, new = Resource.objects.get_or_create(slug=image+'-datasheet', defaults={
                'title': f'{model} — {name}', 'document_type': 'datasheet',
                'description': 'Zoomled datasheet supplied on the NCCT website.',
                'bundled_file': image+'.pdf', 'source_url': 'https://ncctdxb.com/wp-content/'+quote(source),
                'category': outdoor, 'published': True, 'order': order})
            if new: doc.products.add(obj)
        home = Homepage.objects.first()
        ContentPage.objects.get_or_create(slug='about', defaults={'title': 'About NCCT',
            'introduction': home.introduction if home else 'Architectural and professional lighting in Dubai.',
            'body': 'People · Places · Progress\n\nExplore indoor, outdoor, decorative, industrial and professional lighting. Contact the NCCT team in Business Bay, Dubai, to discuss products and project requirements.'})
        # Factual operational notices, not invented contractual terms. Client legal review required.
        defaults = {
            'privacy': ('Privacy information', 'How website enquiries are handled.',
                'The enquiry form records your name, company, email, phone, optional project details, message and consent so the NCCT team can review and respond to your request.\n\nA security token and an anonymised rate-limit record help prevent automated submissions. Access to enquiries is restricted to authorised administrators.\n\nContact NCCT using the contact page for questions about your information or to request correction or deletion.'),
            'cookies': ('Cookie information', 'Cookies used by this website.',
                'This website uses a security cookie to protect form submissions. Administrator sign-in also uses a session cookie. This implementation does not load advertising or analytics trackers.'),
            'terms': ('Website information', 'Product and project enquiries.',
                'Product information and downloadable documents are provided to support enquiries. Confirm the required configuration, specifications and suitability with NCCT before placing an order or finalising a specification.\n\nFor commercial terms, availability and project-specific requirements, contact the NCCT team.'),
        }
        for slug, (title, introduction, body) in defaults.items():
            approved = getattr(home, {'privacy': 'privacy_text', 'cookies': 'cookie_text', 'terms': 'terms_text'}[slug], '') if home else ''
            ContentPage.objects.get_or_create(slug=slug, defaults={'title': title, 'introduction': introduction, 'body': approved or body})
        self.stdout.write(self.style.SUCCESS('Imported reviewed catalogue content. Existing records preserved.'))
