from django.core.management.base import BaseCommand
from apps.notifications.utils import send_email_notification


class Command(BaseCommand):
    help = 'Send queued notifications (placeholder for scheduled tasks)'

    def handle(self, *args, **options):
        # In a real system this would read a queue or DB table to dispatch notifications
        self.stdout.write('No queued notifications to send (placeholder)')
