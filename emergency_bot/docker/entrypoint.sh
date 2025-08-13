#!/bin/bash

set -e

# Wait for database
if [ "$DATABASE_URL" ]; then
  echo "Waiting for database to be ready..."
  python -m scripts.wait_for_db
fi

# Run migrations
echo "Running migrations..."
python manage.py migrate --no-input

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Create superuser if needed
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "Creating superuser..."
  python manage.py createsuperuser --noinput
fi

# Start server based on command
if [ "$1" = "web" ]; then
  echo "Starting Daphne server..."
  daphne -b 0.0.0.0 -p 8000 emergency_bot.asgi:application

elif [ "$1" = "worker" ]; then
  echo "Starting Celery worker..."
  celery -A emergency_bot worker --loglevel=info

elif [ "$1" = "beat" ]; then
  echo "Starting Celery beat..."
  celery -A emergency_bot beat --loglevel=info

else
  echo "Running command: $@"
  exec "$@"
fi 