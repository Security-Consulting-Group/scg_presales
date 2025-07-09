#!/bin/sh

echo '======> Running collectstatic...'
python manage.py collectstatic --no-input --settings=core.settings.production

echo '\n======> Applying migrations...'
python manage.py makemigrations --settings=core.settings.production
python manage.py migrate --settings=core.settings.production

echo '\n======> Running server...'
gunicorn --env DJANGO_SETTINGS_MODULE=core.settings.production core.wsgi:application --bind 0.0.0.0:8000 --workers 1