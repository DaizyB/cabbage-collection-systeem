from django.core.mail import send_mail
from django.conf import settings


def send_email_notification(subject, body, to):
    # Simple wrapper; in prod configure SMTP env vars
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com', [to])


def send_sms_placeholder(number, message):
    # TODO: integrate SMS provider like Twilio. Placeholder for PA scheduled tasks.
    print(f"SMS to {number}: {message}")
