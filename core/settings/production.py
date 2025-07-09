"""
Production settings for SCG Presales project.
"""
import os
from .base import *

# Load environment variables
from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env' / 'production.env')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',') + ['159.65.239.205']

# Add whitenoise middleware for static files
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Production Secret Key
SECRET_KEY = os.environ.get('SECRET_KEY_PROD')
if not SECRET_KEY:
    raise ValueError(
        "SECRET_KEY_PROD environment variable is required in production"
    )

# Database - PostgreSQL for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}

# Email settings for production - Microsoft 365 via Graph API
EMAIL_BACKEND = 'django_o365mail.EmailBackend'
O365_MAIL_CLIENT_ID = os.environ.get('O365_MAIL_CLIENT_ID')
O365_MAIL_CLIENT_SECRET = os.environ.get('O365_MAIL_CLIENT_SECRET')
O365_MAIL_TENANT_ID = os.environ.get('O365_MAIL_TENANT_ID')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@securitygroupcr.com')

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# Static files for production
STATIC_ROOT = os.environ.get('STATIC_ROOT', BASE_DIR / 'staticfiles')

# Whitenoise settings for static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files for production
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', BASE_DIR / 'media')

# # Cache for production - Redis
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.redis.RedisCache',
#         'LOCATION': os.environ.get(
#             'REDIS_URL', 'redis://127.0.0.1:6379/1'
#         ),
#     }
# }

# Production logging - adjusted for Docker
LOGGING['handlers']['file']['filename'] = os.environ.get(
    'LOG_FILE', '/app/logs/scg_presales.log'
)

# # Admin settings
# ADMINS = [
#     (
#         'SCG Admin',
#         os.environ.get('ADMIN_EMAIL', 'admin@securitygroupcr.com')
#     ),
# ]
# MANAGERS = ADMINS