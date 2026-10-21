#!/bin/sh
set -e

mkdir -p /app/data /app/logs
chown -R appuser:appuser /app/data /app/logs 2>/dev/null || true
chmod -R 775 /app/data /app/logs 2>/dev/null || true

gosu appuser alembic upgrade head

exec gosu appuser "$@"
