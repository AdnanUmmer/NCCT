from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from enquiries.models import RateWindow

class Command(BaseCommand):
    help = 'Remove expired anti-spam counters; schedule daily. Does not delete enquiries.'
    def handle(self, *args, **options):
        count,_ = RateWindow.objects.filter(created_at__lt=timezone.now()-timedelta(days=1)).delete()
        self.stdout.write(f'Removed {count} expired counters.')
