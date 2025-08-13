import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-ReplaceThisWithYourOwnSecretKey'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*', 'gaddisa.hdmsoftwaresolutions.com']  # Allow all hosts in development and production domain

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bot',  # Our app
    'emergency_bot.accounts',
    'emergency_bot.agencies',
    'emergency_bot.reports',
    'emergency_bot.notifications',
    'emergency_bot.frontend',
    'emergency_bot.telegram_bot',
    'rest_framework',
    'corsheaders',
    'channels',
    'django_filters',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'emergency_bot.accounts.middleware.TelegramAuthMiddleware',
]

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True  # Allow all origins in development
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "https://web.telegram.org",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://gaddisa.hdmsoftwaresolutions.com",
]
# Allow ngrok domains
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.ngrok\.io$",
    r"^https://.*\.ngrok-free\.app$",
]

ROOT_URLCONF = 'emergency_bot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'emergency_bot/frontend/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'emergency_bot.wsgi.application'
ASGI_APPLICATION = 'emergency_bot.asgi.application'

# Channel layers for WebSockets
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
        # Use Redis in production:
        # 'BACKEND': 'channels_redis.core.RedisChannelLayer',
        # 'CONFIG': {
        #     "hosts": [('127.0.0.1', 6379)],
        # },
    },
}

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = []

# Internationalization
LANGUAGE_CODE = 'en'

TIME_ZONE = 'Africa/Addis_Ababa'

USE_I18N = True
USE_L10N = True
USE_TZ = True

# Language settings
from django.utils.translation import gettext_lazy as _
LANGUAGES = [
    ('en', _('English')),
    ('am', _('Amharic')),
    ('om', _('Afaan Oromo')),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Telegram Bot Settings
TELEGRAM_BOT_TOKEN = '7697446317:AAGfXeRSQqbqdmZOg5KqkyzY7ZuSONLPdrU'  # Updated bot token

# Encryption key for sensitive data (generate with: base64.urlsafe_b64encode(os.urandom(32)).decode())
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', 'VupN3fmyblg7uKkum-NBK6QmdlyRvj_BxP3HCDVFAgg=')

# Security settings for Telegram WebApp
CSRF_TRUSTED_ORIGINS = [
    'https://*.ngrok.io',
    'https://*.ngrok-free.app',
    'https://web.telegram.org',
    'https://gaddisa.hdmsoftwaresolutions.com',
]
