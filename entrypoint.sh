#!/bin/sh

# Set Django settings module for production
export DJANGO_SETTINGS_MODULE=core.settings.production

echo '======> Running collectstatic...'
python manage.py collectstatic --no-input

echo '\n======> Applying migrations...'
python manage.py makemigrations
python manage.py migrate

echo '\n======> Running server...'
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 1