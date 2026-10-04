import logging
from django.core import signing
from django.db import DatabaseError, IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST
from .forms import EnquiryForm
from .notifications import notify
from .models import Enquiry
from .security import issue_token, read_token, rate_allowed, fingerprint, verify_bot_challenge

logger = logging.getLogger(__name__)

@require_GET
@never_cache
@ensure_csrf_cookie
def token(request): return JsonResponse({'token': issue_token()})

@require_POST
@never_cache
def submit(request):
    form = EnquiryForm(request.POST)
    status = 400
    success = False
    try:
        if not rate_allowed(request):
            form.is_valid()
            form.add_error(None, 'Too many attempts. Please wait 10 minutes or contact us by email.')
            status = 429
        elif form.is_valid():
            try:
                submission_id = read_token(form.cleaned_data['token'])
                if form.cleaned_data['website'] or not verify_bot_challenge(request):
                    raise ValueError('Unable to submit this enquiry. Please contact us by email.')
            except (signing.BadSignature, KeyError, TypeError):
                form.add_error(None, 'Your form has expired. Reload the page and try again.')
            except ValueError as error:
                form.add_error(None, str(error))
            else:
                digest = fingerprint(form.cleaned_data)
                try:
                    with transaction.atomic():
                        enquiry = form.save(commit=False)
                        enquiry.submission_id = submission_id
                        enquiry.fingerprint = digest
                        enquiry.source_page = '/'
                        enquiry.save()
                        transaction.on_commit(lambda: notify(enquiry))
                except IntegrityError:
                    if not Enquiry.objects.filter(submission_id=submission_id).exists() and not Enquiry.objects.filter(fingerprint=digest).exists():
                        raise
                success = True
    except DatabaseError:
        logger.error('Enquiry storage unavailable', exc_info=True)
        form.is_valid()
        form.add_error(None, 'We could not save your enquiry. Please try again or email info@ncctdxb.com.')
        status = 503
    if request.headers.get('Accept') == 'application/json':
        response = JsonResponse({'ok':success, 'message':'Thank you. Your enquiry has been received.'} if success else
                                {'ok':False, 'errors':form.errors.get_json_data()}, status=200 if success else status)
        if status == 429: response['Retry-After'] = '600'
        return response
    if success: return redirect('/?enquiry=sent#contact')
    from core.views import home
    return home(request, form=form, form_status=status)
