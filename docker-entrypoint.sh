#!/bin/bash

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Creating super user
echo "Creating super user"
python manage.py createsuperuser --email a@a.com --no-input

# Loading database"
echo "Loading database"
python manage.py loaddata 'store.json'

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000