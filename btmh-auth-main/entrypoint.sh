#!/bin/sh
set -e

echo "Waiting for postgres..."
until nc -z $DB_HOST $DB_PORT; do
  sleep 2
done

echo "Postgres is up - running makemigrations + migrate"
# sinh migrations cho tất cả apps
python manage.py makemigrations --noinput
# áp dụng migrations
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

exec "$@"
