from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Homepage, Capability
from products.models import Category, Product
from projects.models import Project

class Command(BaseCommand):
    help = 'Load source-backed starter content without overwriting admin edits.'

    @transaction.atomic
    def handle(self, *args, **options):
        Homepage.objects.get_or_create(pk=1, defaults={'static_image':'single-light-v2','image_alt':'Concept image of a single bronze pendant casting warm light onto stone','hero_caption':'Single light study / Generated concept','hero_copy':'Considered lighting for architecture.\nFrom a single detail to the entire space.'})
        categories = [
            ('Indoor lighting','Light for interiors, from the ambient layer to the architectural detail.','homepg-6','Warm living room with perimeter ceiling lighting','indoor_lights'),
            ('Outdoor lighting','Light that gives exterior spaces a clear sense of place.','homepg-2','Illuminated steps and curved garden paths','Outdoor_lights'),
            ('Decorative lighting','Distinctive light, as part of the interior composition.','homepg-4','Interior with pendant and integrated linear lighting','Decorative_lights'),
            ('Industrial lighting','Explore the industrial lighting selection with our team.','indus_p1','Black suspended industrial-style luminaire','industrial_lights'),
            ('Professional lighting','Discover lighting for professional applications.','prof_p1','Professional lighting equipment from the NCCT catalogue','professional_lights')]
        saved = []
        for order,(name,description,image,alt,slug) in enumerate(categories):
            obj,_ = Category.objects.get_or_create(name=name, defaults={'description':description,'static_image':image,'image_alt':alt,'source_url':f'https://ncctdxb.com/en/Real/{slug}.html','order':order})
            saved.append(obj)
        for order,(title,application,image,alt) in enumerate([
            ('The architecture of atmosphere','Interior lighting','homepg-4','Warm open-plan interior with linear ceiling lighting and pendant fixtures'),
            ('A path, quietly defined','Outdoor lighting','homepg-2','Curved outdoor steps defined by warm linear lighting'),
            ('After the sun goes down','Landscape lighting','homepg-3','Terraced garden and trees illuminated after dark')]):
            Project.objects.get_or_create(title=title,defaults={'application':application,'static_image':image,'image_alt':alt,'source_url':'https://ncctdxb.com/en/index.html','order':order,'attribution_verified':False})
        for order,(title,description) in enumerate([
            ('Light & architecture','Light can reveal a surface, emphasise a form or give a space a new character. Explore NCCT lighting for architectural settings.'),
            ('Inside & outside','NCCT presents lighting for both interior spaces and exterior environments, with dedicated indoor and outdoor collections.'),
            ('A personal lighting expression','The NCCT website describes flexible LED forms that can be combined into personalised lighting systems. Discuss your intended application with our team.'),
            ('Across applications','Discover indoor, outdoor, decorative, industrial and professional lighting through the NCCT portfolio.')]):
            Capability.objects.get_or_create(title=title,defaults={'description':description,'order':order})
        for order,(name,cat,image,description,alt) in enumerate([
            ('Ceiling lighting',saved[0],'ind_p1','A selection from the indoor collection.','Round black ceiling fixture with a diffuse face'),
            ('Wall lighting',saved[0],'ind_p3','Light as an interior detail.','Warm wall-mounted decorative light'),
            ('Pendant lighting',saved[3],'indus_p1','A selection from the industrial collection.','Black industrial pendant light on a chain')]):
            Product.objects.get_or_create(name=name,defaults={'category':cat,'static_image':image,'image_alt':alt,'description':description,'source_url':cat.source_url,'verified':True,'order':order})
        self.stdout.write(self.style.SUCCESS('Homepage content ready. No existing content overwritten.'))
