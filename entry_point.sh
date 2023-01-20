#!/bin/sh

echo "Running migrations"
python manage.py migrate

echo "Starting Server"
gunicorn --bind 0.0.0.0:8000 project.wsgi
