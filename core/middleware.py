from django.conf import settings
from django.db import DatabaseError
from django.http import HttpResponse
from enquiries.security import rate_allowed


class AdminLoginRateLimit:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/admin/login/' and request.method == 'POST':
            try:
                allowed = rate_allowed(request, scope='admin-login', limit=settings.ADMIN_LOGIN_RATE_LIMIT)
            except DatabaseError:
                return HttpResponse('Sign-in is temporarily unavailable. Please try again shortly.', status=503)
            if not allowed:
                response = HttpResponse('Too many sign-in attempts. Please wait 10 minutes and try again.', status=429)
                response['Retry-After'] = '600'
                return response
        return self.get_response(request)
