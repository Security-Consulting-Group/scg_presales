#!/bin/sh

# Set Django settings module for production
export DJANGO_SETTINGS_MODULE=core.settings.production

echo '======> Running collectstatic...'
python manage.py collectstatic --no-input

echo '\n======> Applying migrations...'
python manage.py makemigrations

# Try to run migrations with retry logic
echo 'Running database migrations...'
for i in 1 2 3 4 5; do
    echo "Migration attempt $i..."
    if python manage.py migrate; then
        echo "Migrations completed successfully"
        break
    else
        echo "Migration failed, retrying in 5 seconds..."
        sleep 5
    fi
    if [ $i -eq 5 ]; then
        echo "ERROR: Migrations failed after 5 attempts. Check database permissions."
        echo "Continuing with server startup..."
    fi
done

echo '\n======> Running server...'
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 1