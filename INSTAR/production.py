"""Configuración de Render y Supabase; el desarrollo local usa settings.py."""
import os
from urllib.parse import urlsplit

import dj_database_url
from botocore.config import Config
from django.core.exceptions import ImproperlyConfigured

from .settings import *  # noqa: F403


def required(name):
    value = os.environ.get(name, '').strip()
    if not value:
        raise ImproperlyConfigured(f'Falta configurar {name}.')
    return value


def https_origin(value, name):
    url = urlsplit(value)
    if (url.scheme != 'https' or not url.hostname or url.username or url.password
            or url.path not in ('', '/') or url.query or url.fragment):
        raise ImproperlyConfigured(f'{name} debe ser un origen HTTPS sin rutas ni credenciales.')
    return f'https://{url.netloc}'


DEBUG = False
SECRET_KEY = required('DJANGO_SECRET_KEY')
if SECRET_KEY.startswith('django-insecure-') or len(SECRET_KEY) < 50:
    raise ImproperlyConfigured('DJANGO_SECRET_KEY debe ser una clave nueva de al menos 50 caracteres.')

PUBLIC_SITE_URL = https_origin(required('PUBLIC_SITE_URL'), 'PUBLIC_SITE_URL')
ALLOWED_HOSTS = [urlsplit(PUBLIC_SITE_URL).hostname]
CSRF_TRUSTED_ORIGINS = [PUBLIC_SITE_URL]
render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '').strip()
if render_host:
    render_origin = https_origin(f'https://{render_host}', 'RENDER_EXTERNAL_HOSTNAME')
    ALLOWED_HOSTS.append(urlsplit(render_origin).hostname)
    CSRF_TRUSTED_ORIGINS.append(render_origin)

database_url = required('DATABASE_URL')
if urlsplit(database_url).scheme not in ('postgres', 'postgresql'):
    raise ImproperlyConfigured('DATABASE_URL debe ser una conexión PostgreSQL de Supabase.')
DATABASES = {'default': dj_database_url.parse(
    database_url, conn_max_age=60, conn_health_checks=True, ssl_require=True,
)}
DATABASES['default']['DISABLE_SERVER_SIDE_CURSORS'] = True
DATABASES['default'].setdefault('OPTIONS', {}).update({
    'options': '-c search_path=instar',
    'prepare_threshold': None,
})

MIDDLEWARE = list(MIDDLEWARE)  # noqa: F405
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
MIDDLEWARE.append('INSTAR.deployment.PrivateResponsesMiddleware')
STATIC_ROOT = BASE_DIR / 'staticfiles'  # noqa: F405

endpoint = required('SUPABASE_S3_ENDPOINT')
endpoint_url = urlsplit(endpoint)
if (endpoint_url.scheme != 'https' or not endpoint_url.hostname
        or endpoint_url.username or endpoint_url.password or endpoint_url.query
        or endpoint_url.fragment or endpoint_url.path.rstrip('/') != '/storage/v1/s3'):
    raise ImproperlyConfigured('SUPABASE_S3_ENDPOINT debe ser el endpoint HTTPS S3 de Supabase.')

STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3.S3Storage',
        'OPTIONS': {
            'access_key': required('SUPABASE_S3_ACCESS_KEY_ID'),
            'secret_key': required('SUPABASE_S3_SECRET_ACCESS_KEY'),
            'bucket_name': os.environ.get('SUPABASE_STORAGE_BUCKET', 'instar-media'),
            'endpoint_url': endpoint.rstrip('/'),
            'region_name': required('SUPABASE_STORAGE_REGION'),
            'addressing_style': 'path',
            'signature_version': 's3v4',
            'client_config': Config(
                signature_version='s3v4', s3={'addressing_style': 'path'},
                request_checksum_calculation='when_required',
                response_checksum_validation='when_required',
            ),
            'default_acl': None,
            'file_overwrite': False,
            'querystring_auth': True,
            'querystring_expire': 900,
        },
    },
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}

# Render termina HTTPS y transmite el protocolo al servidor de aplicación.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# La aplicación actual no envía correo. SMTP se configura cuando se habilite.
MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
        'OPTIONS': {
            'host': os.environ.get('EMAIL_HOST', 'localhost'),
            'port': int(os.environ.get('EMAIL_PORT', '587')),
            'username': os.environ.get('EMAIL_HOST_USER', ''),
            'password': os.environ.get('EMAIL_HOST_PASSWORD', ''),
            'use_tls': True,
        },
    },
}
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'webmaster@localhost')
