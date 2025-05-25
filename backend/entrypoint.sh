#!/bin/sh

# Wait for Postgres to be ready
until nc -z db 5432; do
  echo "Waiting for postgres..."
  sleep 0.5
done

echo "PostgreSQL started"

exec "$@"
