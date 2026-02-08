"""Single-file Django settings for the project.

This consolidates previous package-style settings into one file to simplify
deployments (e.g., PythonAnywhere). Behavior:
- Uses `DJANGO_ENV` environment variable to select 'dev' (default) or 'prod'.
- In `prod` mode, critical environment variables (like `DJ_SECRET_KEY`) are required.
- Defaults to SQLite for local development.

Security: do not commit secrets; supply via environment variables in production.
"""
from pathlib import Path
import os
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent


def env(key: str, default: Any = None, required: bool = False):
    v = os.environ.get(key, default)
    if required and (v is None or v == ''):
        raise RuntimeError(f'Missing required environment variable: {key}')
    return v


# Environment selection
DJANGO_ENV = env('DJANGO_ENV', 'dev').lower()

# Core
SECRET_KEY = env('DJ_SECRET_KEY', 'unsafe-dev-key' if DJANGO_ENV == 'dev' else None)
DEBUG = DJANGO_ENV == 'dev'

if DJANGO_ENV == 'prod' and not SECRET_KEY:
    raise RuntimeError('DJ_SECRET_KEY must be set in production')

ALLOWED_HOSTS = env('DJ_ALLOWED_HOSTS', '*').split(',') if env('DJ_ALLOWED_HOSTS') else ['*']

# Applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'apps.accounts',
    'apps.customers',
    'apps.collectors',
    'apps.pickups',
    'apps.payments',
    'apps.careers',
    'apps.quizzes',
    'apps.notifications',
    'apps.reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'trash_mgmt.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'trash_mgmt.wsgi.application'

AUTH_USER_MODEL = 'accounts.User'

# Database: default to sqlite for dev; in prod allow env override via DATABASE_URL
DATABASES = {}
if env('DATABASE_URL'):
    # simple DATABASE_URL parsing (postgres example): postgres://USER:PASS@HOST:PORT/NAME
    url = env('DATABASE_URL')
    if url.startswith('postgres'):
        # minimal parsing — for full support use dj-database-url
        import urllib.parse as up

        parsed = up.urlparse(url)
        DATABASES['default'] = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': parsed.path.lstrip('/'),
            'USER': parsed.username,
            'PASSWORD': parsed.password,
            'HOST': parsed.hostname,
            'PORT': parsed.port or '',
        }
else:
    DATABASES['default'] = {'ENGINE': 'django.db.backends.sqlite3', 'NAME': str(BASE_DIR / 'db.sqlite3')}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email defaults
if DJANGO_ENV == 'dev':
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = env('EMAIL_HOST', '')
    EMAIL_PORT = int(env('EMAIL_PORT', 587)) if env('EMAIL_PORT') else 587
    EMAIL_HOST_USER = env('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', '')
    EMAIL_USE_TLS = env('EMAIL_USE_TLS', '1') == '1'

# Security settings for production
if DJANGO_ENV == 'prod':
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

