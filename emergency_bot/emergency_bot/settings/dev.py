"""
Development settings for the Emergency Reporting System project.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# INSTALLED_APPS += ["debug_toolbar"]
# MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True

# Debug toolbar settings
# INTERNAL_IPS = ["127.0.0.1"]

# Turn off password validation in development
AUTH_PASSWORD_VALIDATORS = []

# Disable HTTPS requirements in development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# Use console backend for emails in development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Create logs directory if it doesn't exist
try:
    os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)
except:
    pass 