#!/usr/bin/env bash
set -euo pipefail
python -m pip install -r requirements-production.txt
python manage.py collectstatic --noinput
python manage.py prepare_database
python manage.py migrate --noinput
python manage.py bootstrap_data
