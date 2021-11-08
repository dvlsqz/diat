#!/bin/sh
set -e

if [ "x$DJANGO_MANAGEPY_MIGRATE" = 'xon' ]; then
    /venv/bin/python manage.py migrate --noinput
    /venv/bin/python manage.py loaddata groups
    /venv/bin/python manage.py createsu
    /venv/bin/python manage.py loaddata dietas
    /venv/bin/python manage.py loaddata servicios
    /venv/bin/python manage.py loaddata jornadas
fi

if [ "x$DJANGO_MANAGEPY_COLLECTSTATIC" = 'xon' ]; then
    /venv/bin/python manage.py collectstatic --noinput
fi

exec "$@"