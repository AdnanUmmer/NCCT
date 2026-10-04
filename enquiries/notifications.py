import logging
from django.conf import settings
from django.core.mail import send_mail


def notify(enquiry):
    if not settings.ENQUIRY_NOTIFICATION_EMAIL or not settings.EMAIL_HOST:
        return
    try:
        send_mail('New NCCT website enquiry',
                  f'An enquiry from {enquiry.company_name} has been saved.\nReview it in the secure admin: {settings.SITE_URL}/admin/enquiries/enquiry/{enquiry.pk}/change/',
                  settings.DEFAULT_FROM_EMAIL, [settings.ENQUIRY_NOTIFICATION_EMAIL])
    except Exception:
        # Never roll back a saved enquiry when SMTP fails.
        logging.getLogger(__name__).exception('Enquiry saved but notification delivery failed')
