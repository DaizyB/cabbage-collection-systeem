
import os
from pathlib import Path
from typing import Any
from dotenv import load_dotenv
import warnings

BASE_DIR = Path(__file__).resolve().parent.parent

ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE, override=True)
else:
    if os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("CI") == "true":
        
        pass
    else:
        warnings.warn(f".env file not found at {ENV_FILE}; continuing without it. "
                      "Set environment variables or create a .env for local development.")

def env(key: str, default: Any = None, required: bool = False):
    value = os.environ.get(key, default)
    if required and (value is None or value == ''):
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value




BASE_DIR = Path(__file__).resolve().parent.parent

DJANGO_ENV = env('DJANGO_ENV', 'dev')

SECRET_KEY = env('DJ_SECRET_KEY', 'unsafe-dev-key')

if DJANGO_ENV == 'prod' and SECRET_KEY == 'unsafe-dev-key':
    raise RuntimeError("DJ_SECRET_KEY must be set in production")



DEBUG = True if DJANGO_ENV == 'dev' else False

GOOGLE_MAPS_API_KEY = env('GOOGLE_MAPS_API_KEY', '')


_allowed = env('DJ_ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [h.strip() for h in _allowed.split(',') if h.strip()] if _allowed else ['*']

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
    'apps.collectors.apps.CollectorsConfig',
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

AUTH_USER_MODEL = 'accounts.User'

DATABASES = {}

DATABASE_URL = env('DATABASE_URL')

if DATABASE_URL:
    import urllib.parse as up

    parsed = up.urlparse(DATABASE_URL)
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': parsed.path.lstrip('/'),
        'USER': parsed.username,
        'PASSWORD': parsed.password,
        'HOST': parsed.hostname,
        'PORT': parsed.port or '',
    }
else:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }

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
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

if DJANGO_ENV == 'dev':
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = env('EMAIL_HOST', '')
    EMAIL_PORT = int(env('EMAIL_PORT', 587))
    EMAIL_HOST_USER = env('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', '')
    EMAIL_USE_TLS = env('EMAIL_USE_TLS', '1') == '1'

if DJANGO_ENV == 'prod':
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


try:
    import dotenv
except ImportError:
    import pip
    pip.main(['install', 'python-dotenv'])
