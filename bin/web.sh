#!/usr/bin/env bash
# Start the web server (used by Appliku).
set -euo pipefail
python manage.py collectstatic --noinput
exec gunicorn config.wsgi --bind "0.0.0.0:${PORT:-8000}" --workers "${WEB_CONCURRENCY:-3}" --access-logfile - --log-file -
