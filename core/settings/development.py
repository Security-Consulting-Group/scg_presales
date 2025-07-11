"""
Development settings for SCG Presales project.
"""
import os
from .base import *

# Load environment variables
from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env' / 'development.env')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Development specific settings
SECRET_KEY = os.environ.get('SECRET_KEY_DEV')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY_DEV environment variable is required")

# Database - SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email settings for development - Print to console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Business configuration for SCG
COMPANY_NAME = 'Security Consulting Group'
COMPANY_PHONE = '+506 1234-5678'
COMPANY_EMAIL = 'services@securitygroupcr.com'
COMPANY_ADDRESS = 'San José, Costa Rica'
COMPANY_WHATSAPP = 'https://wa.me/50612345678'
COMPANY_LINKEDIN = 'https://www.linkedin.com/company/securitygroupcr/'

# Sales configuration
SALES_EMAIL = 'ijgr11@gmail.com'

DEFAULT_FROM_EMAIL = 'SCG Presales <noreply@securitygroupcr.com>'