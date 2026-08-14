#!/usr/bin/env bash
# Script que corre Render en cada despliegue.
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Crea el superusuario admin usando variables de entorno (Render free no tiene Shell).
# "|| true" evita que el build falle si ya existe (username duplicado) en el siguiente deploy.
python manage.py createsuperuser --no-input || true
