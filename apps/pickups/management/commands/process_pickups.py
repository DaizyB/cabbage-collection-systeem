from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.pickups.models import Pickup


class Command(BaseCommand):
    help = 'Process scheduled pickups: mark overdue pickups as failed and optionally notify collectors.'

    def handle(self, *args, **options):
        now = timezone.now()
        due = Pickup.objects.filter(state=Pickup.STATE_SCHEDULED, scheduled_time__lte=now)
        count = 0
        for p in due:
            # In a minimal free-tier environment we just mark as failed or leave for manual assignment.
            p.fail()
            count += 1
        self.stdout.write(self.style.SUCCESS(f'Processed {count} pickups'))
