#!/usr/bin/env bash
# Start the web server (used by Appliku). Static files are collected during the Appliku build.
set -euo pipefail
exec gunicorn config.wsgi --bind "0.0.0.0:${PORT:-8000}" --workers "${WEB_CONCURRENCY:-3}" --access-logfile - --log-file -
