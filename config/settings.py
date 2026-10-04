import os
import secrets
from pathlib import Path
import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured('Set DJANGO_SECRET_KEY, or DJANGO_DEBUG=1 for local development.')
    SECRET_KEY = secrets.token_urlsafe(50)
ALLOWED_HOSTS = [host.strip() for host in os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if host.strip()]
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',') if origin.strip()]
SITE_URL = os.environ.get('SITE_URL', 'https://ncctdxb.com').rstrip('/')
INSTALLED_APPS = ['django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
                  'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
                  'core', 'projects', 'products', 'enquiries']
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware', 'whitenoise.middleware.WhiteNoiseMiddleware',
              'django.contrib.sessions.middleware.SessionMiddleware', 'django.middleware.common.CommonMiddleware',
              'django.middleware.csrf.CsrfViewMiddleware', 'django.contrib.auth.middleware.AuthenticationMiddleware',
              'core.middleware.AdminLoginRateLimit', 'django.contrib.messages.middleware.MessageMiddleware', 'django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF = 'config.urls'
TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [BASE_DIR/'templates'],
              'APP_DIRS': True, 'OPTIONS': {'context_processors': ['django.template.context_processors.request',
              'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages', 'core.context_processors.site_content']}}]
WSGI_APPLICATION = 'config.wsgi.application'
DATABASES = {'default': dj_database_url.config(default=f'sqlite:///{BASE_DIR / "db.sqlite3"}', conn_max_age=60)}
AUTH_PASSWORD_VALIDATORS = [{'NAME': f'django.contrib.auth.password_validation.{name}'} for name in
    ['UserAttributeSimilarityValidator', 'MinimumLengthValidator', 'CommonPasswordValidator', 'NumericPasswordValidator']]
LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Asia/Dubai'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR/'staticfiles'
STATICFILES_DIRS = [BASE_DIR/'static']
STORAGES = {'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
            'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'}}
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR/'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
DATA_UPLOAD_MAX_MEMORY_SIZE = 64 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
# Render enforces HTTPS at its edge. Do not redirect again inside Django,
# even if an older deployment still sets DJANGO_SSL_REDIRECT=1.
ON_RENDER = os.environ.get('RENDER') == 'true'
SECURE_SSL_REDIRECT = False if ON_RENDER else os.environ.get('DJANGO_SSL_REDIRECT', '0' if DEBUG else '1') == '1'
SECURE_HSTS_SECONDS = int(os.environ.get('DJANGO_HSTS_SECONDS', '0'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get('DJANGO_HSTS_INCLUDE_SUBDOMAINS', '0') == '1'
SECURE_HSTS_PRELOAD = os.environ.get('DJANGO_HSTS_PRELOAD', '0') == '1'
# Render terminates TLS before forwarding requests to Django. Recognise the
# original scheme so SecurityMiddleware does not redirect HTTPS back to itself.
# Retain the explicit opt-in for other trusted reverse-proxy deployments.
if ON_RENDER or os.environ.get('DJANGO_TRUST_PROXY_SSL') == '1':
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
ENQUIRY_MIN_SECONDS = 3
ENQUIRY_RATE_LIMIT = 10
# Optional dotted callable(request) -> bool; integrate Turnstile verification here.
ENQUIRY_BOT_VERIFIER = ''
CSRF_FAILURE_VIEW = 'core.views.csrf_failure'

# Public indexing is an explicit launch decision; previews remain noindex.
SITE_INDEXABLE = os.environ.get('SITE_INDEXABLE', '0') == '1'
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', '1') == '1'
EMAIL_TIMEOUT = 10
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'webmaster@localhost')
ENQUIRY_NOTIFICATION_EMAIL = os.environ.get('ENQUIRY_NOTIFICATION_EMAIL', '')
# Optional persistent S3-compatible storage for Render's ephemeral instances.
if os.environ.get('AWS_STORAGE_BUCKET_NAME'):
    STORAGES['default'] = {'BACKEND': 'storages.backends.s3.S3Storage', 'OPTIONS': {
        'bucket_name': os.environ['AWS_STORAGE_BUCKET_NAME'],
        'endpoint_url': os.environ.get('AWS_S3_ENDPOINT_URL') or None,
        'region_name': os.environ.get('AWS_S3_REGION_NAME') or None,
        'default_acl': None, 'file_overwrite': False,
        'object_parameters': {'CacheControl': 'max-age=86400'},
    }}
MEDIA_ROOT = Path(os.environ.get('MEDIA_ROOT', str(BASE_DIR / 'media')))

ADMIN_LOGIN_RATE_LIMIT = int(os.environ.get('ADMIN_LOGIN_RATE_LIMIT', '20'))
