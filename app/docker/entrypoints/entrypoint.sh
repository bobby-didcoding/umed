#!/bin/sh

python manage.py makemigrations
python manage.py migrate
python manage.py loaddata care_providers.yaml users.yaml studies.yaml patients.yaml
pytest
exec "$@"