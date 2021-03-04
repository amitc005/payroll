#!/bin/bash

echo "Apply database migrations"
python manage.py makemigrations --noinput
python manage.py migrate

echo "Running parking rate server"
python manage.py runserver 0.0.0.0:8000
