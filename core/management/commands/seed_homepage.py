from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from core.models import Homepage, Capability, HomepageSeedState
from products.models import Category, Product
from projects.models import Project

class Command(BaseCommand):
    help = 'Load source-backed starter content without overwriting admin edits.'

    @transaction.atomic
    def handle(self, *args, **options):
        # The unique receipt serializes concurrent initializers and rolls back
        # with the content on failure. Never match renamed content on later runs.
        _, created = HomepageSeedState.objects.get_or_create(key='homepage-v1')
        if not created:
            self.stdout.write(self.style.SUCCESS('Homepage already initialized; no records changed.'))
            return
        # Treat populated sections as administrator-owned, including on legacy
        # deployments that predate the receipt. Do not infer missing seed rows.
        initialize = {model: not model.objects.exists() for model in (Category, Project, Capability, Product)}
        for model, empty in initialize.items():
            if not empty:
                self.stdout.write(f'Preserving existing {model.__name__} records.')
        Homepage.objects.get_or_create(pk=1, defaults={'static_image':'hero','image_alt':'Architectural luminaires against dark stone with warm integrated lighting','hero_caption':'Architectural lighting, considered in context','hero_copy':'Considered lighting for architecture.\nFrom a single detail to the entire space.'})
        categories = [
            ('Indoor lighting','Light for interiors, from the ambient layer to the architectural detail.','homepg-6','Warm living room with perimeter ceiling lighting','indoor_lights'),
            ('Outdoor lighting','Light that gives exterior spaces a clear sense of place.','outside','Exterior path and landscape illuminated with warm architectural lighting','Outdoor_lights'),
            ('Decorative lighting','Distinctive light, as part of the interior composition.','homepg-4','Interior with pendant and integrated linear lighting','Decorative_lights'),
            ('Industrial lighting','Explore the industrial lighting selection with our team.','industrial','Modern industrial lighting in a high-bay warehouse','industrial_lights'),
            ('Professional lighting','Discover lighting for professional applications.','professional','Professional studio lighting equipment in a production space','professional_lights')]
        saved = []
        for order,(name,description,image,alt,slug) in enumerate(categories):
            if initialize[Category]:
                obj,_ = Category.objects.get_or_create(name=name, defaults={'description':description,'static_image':image,'image_alt':alt,'source_url':f'https://ncctdxb.com/en/Real/{slug}.html','order':order})
            else:
                obj = Category.objects.filter(name=name).first()
            saved.append(obj)
        for order,(title,application,image,alt) in enumerate([
            ('The architecture of atmosphere','Interior lighting','architecture','Warm architectural interior with sculptural lighting and illuminated landscape'),
            ('A path, quietly defined','Outdoor lighting','street','Illuminated city street and skyline at night'),
            ('After the sun goes down','Landscape lighting','sundown','Garden terraces illuminated after sunset')]):
            if initialize[Project]:
                Project.objects.get_or_create(title=title,defaults={'application':application,'static_image':image,'image_alt':alt,'source_url':'https://ncctdxb.com/en/index.html','order':order,'attribution_verified':False,'featured':True})
        for order,(title,description) in enumerate([
            ('Light & architecture','Light can reveal a surface, emphasise a form or give a space a new character. Explore NCCT lighting for architectural settings.'),
            ('Inside & outside','NCCT presents lighting for both interior spaces and exterior environments, with dedicated indoor and outdoor collections.'),
            ('A personal lighting expression','The NCCT website describes flexible LED forms that can be combined into personalised lighting systems. Discuss your intended application with our team.'),
            ('Across applications','Discover indoor, outdoor, decorative, industrial and professional lighting through the NCCT portfolio.')]):
            if initialize[Capability]:
                Capability.objects.get_or_create(title=title,defaults={'description':description,'order':order})
        for order,(name,cat,image,description,alt) in enumerate([
            ('Ceiling lighting',saved[0],'ind_p1','A selection from the indoor collection.','Round black ceiling fixture with a diffuse face'),
            ('Wall lighting',saved[0],'ind_p3','Light as an interior detail.','Warm wall-mounted decorative light'),
            ('Pendant lighting',saved[3],'indus_p1','A selection from the industrial collection.','Black industrial pendant light on a chain')]):
            if initialize[Product]:
                if cat is None:
                    raise CommandError('Existing categories have been customised. Cannot safely attach starter products. Create the intended products in admin, then rerun. No seed changes were saved.')
                Product.objects.get_or_create(name=name,defaults={'category':cat,'static_image':image,'image_alt':alt,'description':description,'source_url':cat.source_url,'verified':True,'featured':True,'order':order})
        self.stdout.write(self.style.SUCCESS('Homepage initialized. Existing content preserved; future runs will make no changes.'))
