#!/bin/sh

# Wait for Postgres to be ready
until nc -z db 5432; do
  echo "Waiting for postgres..."
  sleep 0.5
done

echo "PostgreSQL started"

# Run Alembic migrations (idempotent)
alembic revision --autogenerate -m "init core tables" || true
alembic upgrade head

# Sync superuser and company data
# python app/create_superuser.py < /dev/null || true
# python app/syncdata.py || true

exec "$@"
