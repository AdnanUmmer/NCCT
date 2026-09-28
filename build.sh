#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

python -m pip install -r requirements.txt
python manage.py check
python manage.py migrate --noinput
python manage.py seed_homepage
python manage.py collectstatic --noinput
