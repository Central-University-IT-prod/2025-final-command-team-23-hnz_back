#!/bin/sh

python ./manage.py migrate
python ./manage.py collectstatic
gunicorn loyalT.wsgi:application --bind REDACTED  --workers 4 --log-level debug
