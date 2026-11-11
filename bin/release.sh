#!/usr/bin/env bash
# Runs once after each deploy: apply migrations, load demo hotels if the database is empty.
set -euo pipefail
python manage.py migrate --noinput
python manage.py seed_escapes
