#!/bin/sh

# Wait for Postgres to be ready
until nc -z db 5432; do
  echo "Waiting for postgres..."
  sleep 0.5
done

echo "PostgreSQL started"

# Thử migrate, nếu lỗi sẽ xóa bảng alembic_version rồi migrate lại (chỉ nên dùng khi thực sự cần thiết)
alembic upgrade head || {
  echo "Alembic migrate failed, trying to reset alembic_version...";
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -h db -c "DROP TABLE IF EXISTS alembic_version CASCADE;" || true
  alembic upgrade head
}

# Sync superuser and company data nếu cần (nên kiểm tra logic tránh trùng lặp)
# python app/create_superuser.py < /dev/null || true
# python app/syncdata.py || true

exec "$@"
