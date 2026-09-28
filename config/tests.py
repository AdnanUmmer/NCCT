"""Deployment regression tests: real settings parsing and proxy/CSRF middleware."""
import os
import runpy
import secrets
from pathlib import Path
from unittest.mock import patch

from django.http import JsonResponse
from django.test import Client, SimpleTestCase, override_settings
from django.urls import path
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie


@ensure_csrf_cookie
@csrf_protect
def probe(request):
    return JsonResponse({'secure': request.is_secure(), 'host': request.get_host()})


urlpatterns = [path('probe/', probe)]


def load_settings(**values):
    environment = {'DJANGO_SECRET_KEY': secrets.token_urlsafe(50), **values}
    with patch.dict(os.environ, environment, clear=True):
        return runpy.run_path(str(Path(__file__).with_name('settings.py')))


class RenderConfigurationTests(SimpleTestCase):
    def test_render_defaults_and_environment_lists(self):
        config = load_settings(RENDER='true', DJANGO_ALLOWED_HOSTS='ncct.onrender.com, design.theadvoxy.com,',
            DJANGO_CSRF_TRUSTED_ORIGINS='https://ncct.onrender.com, https://design.theadvoxy.com,')
        self.assertEqual(config['SECURE_PROXY_SSL_HEADER'], ('HTTP_X_FORWARDED_PROTO', 'https'))
        self.assertTrue(config['SECURE_SSL_REDIRECT'])
        self.assertEqual(config['ALLOWED_HOSTS'], ['ncct.onrender.com', 'design.theadvoxy.com'])
        self.assertEqual(config['CSRF_TRUSTED_ORIGINS'], ['https://ncct.onrender.com', 'https://design.theadvoxy.com'])

    def test_local_development_and_other_proxy_opt_in(self):
        local = load_settings(DJANGO_DEBUG='1')
        self.assertFalse(local['SECURE_SSL_REDIRECT'])
        self.assertNotIn('SECURE_PROXY_SSL_HEADER', local)
        self.assertEqual(local['ALLOWED_HOSTS'], ['localhost', '127.0.0.1'])
        self.assertFalse(local['SESSION_COOKIE_SECURE'])
        self.assertFalse(local['CSRF_COOKIE_SECURE'])
        explicit = load_settings(DJANGO_TRUST_PROXY_SSL='1')
        self.assertEqual(explicit['SECURE_PROXY_SSL_HEADER'], ('HTTP_X_FORWARDED_PROTO', 'https'))
        disabled = load_settings(DJANGO_SSL_REDIRECT='0')
        self.assertFalse(disabled['SECURE_SSL_REDIRECT'])

    def test_both_hosts_https_redirect_and_csrf(self):
        hosts = ['ncct.onrender.com', 'design.theadvoxy.com']
        config = load_settings(RENDER='true', DJANGO_ALLOWED_HOSTS=','.join(hosts),
            DJANGO_CSRF_TRUSTED_ORIGINS=','.join('https://' + host for host in hosts))
        keys = ['ALLOWED_HOSTS', 'CSRF_TRUSTED_ORIGINS', 'SECURE_SSL_REDIRECT', 'SECURE_PROXY_SSL_HEADER',
                'SESSION_COOKIE_SECURE', 'CSRF_COOKIE_SECURE']
        with override_settings(ROOT_URLCONF=__name__, **{key: config[key] for key in keys}):
            client = Client(enforce_csrf_checks=True)
            for host in hosts:
                with self.subTest(host=host):
                    response = client.get('/probe/', HTTP_HOST=host, HTTP_X_FORWARDED_PROTO='http')
                    self.assertEqual(response.status_code, 301)
                    self.assertEqual(response['Location'], f'https://{host}/probe/')
                    response = client.get('/probe/', HTTP_HOST=host, HTTP_X_FORWARDED_PROTO='https')
                    self.assertEqual(response.status_code, 200)
                    self.assertTrue(response.json()['secure'])
                    self.assertEqual(response.json()['host'], host)
                    for origin in hosts:
                        response = client.post('/probe/', {}, HTTP_HOST=host, HTTP_X_FORWARDED_PROTO='https',
                            HTTP_ORIGIN=f'https://{origin}', HTTP_X_CSRFTOKEN=client.cookies['csrftoken'].value)
                        self.assertEqual(response.status_code, 200)
                    response = client.post('/probe/', {}, HTTP_HOST=host, HTTP_X_FORWARDED_PROTO='https',
                        HTTP_ORIGIN='https://untrusted.example', HTTP_X_CSRFTOKEN=client.cookies['csrftoken'].value)
                    self.assertEqual(response.status_code, 403)
