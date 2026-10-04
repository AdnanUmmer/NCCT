import time
import uuid
from django.conf import settings
from django.core import signing
from django.db.models import F
from django.utils.crypto import salted_hmac
from django.utils.module_loading import import_string
from .models import RateWindow

def issue_token():
    return signing.dumps({'id':str(uuid.uuid4()), 'started':time.time()}, salt='enquiry')

def read_token(value):
    data = signing.loads(value, salt='enquiry', max_age=3600)
    if time.time() - data['started'] < settings.ENQUIRY_MIN_SECONDS:
        raise ValueError('Please take a moment to review your details, then submit again.')
    return uuid.UUID(data['id'])

def rate_allowed(request, scope='enquiry', limit=None):
    # REMOTE_ADDR is supplied by the server. Never trust a client-supplied forwarded IP.
    bucket = int(time.time() // 600)
    key = salted_hmac(scope+'-rate', f'{request.META.get("REMOTE_ADDR", "unknown")}:{bucket}').hexdigest()
    window, _ = RateWindow.objects.get_or_create(key=key)
    return bool(RateWindow.objects.filter(pk=window.pk, count__lt=limit if limit is not None else settings.ENQUIRY_RATE_LIMIT).update(count=F('count')+1))

def verify_bot_challenge(request):
    verifier = settings.ENQUIRY_BOT_VERIFIER
    return import_string(verifier)(request) if verifier else True

def fingerprint(data):
    fields = ['name','company_name','email','phone','project_type','message']
    payload = '\x00'.join(str(data.get(k,'')).strip().lower() for k in fields)
    return salted_hmac('enquiry-duplicate', payload, algorithm='sha256').hexdigest()
