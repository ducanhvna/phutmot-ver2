#!/bin/sh

# Wait for Postgres to be ready
until nc -z db 5432; do
  echo "Waiting for postgres..."
  sleep 0.5
done

echo "PostgreSQL started"

# Kiểm tra nếu chưa có migration version nào thì tự động tạo migration
if [ ! "$(ls -A alembic/versions 2>/dev/null)" ]; then
  echo "Chưa có file migration, tự động tạo migration..."
  alembic revision --autogenerate -m "init core tables"
fi

# Kiểm tra bảng etl_jobs đã tồn tại chưa bằng Python + SQLAlchemy
python3 - <<END
import sys, os
from sqlalchemy import create_engine, inspect

db_url = os.getenv("DATABASE_URL") or f"postgresql://{os.getenv('POSTGRES_USER','postgres')}:{os.getenv('POSTGRES_PASSWORD','postgres')}@db:5432/{os.getenv('POSTGRES_DB','postgres')}"
engine = create_engine(db_url)
inspector = inspect(engine)
if "etl_jobs" in inspector.get_table_names():
    print("Bảng etl_jobs đã tồn tại.")
    sys.exit(0)
else:
    print("Bảng etl_jobs chưa tồn tại, sẽ migrate...")
    sys.exit(1)
END

if [ $? -ne 0 ]; then
  alembic upgrade head
fi

# Sync superuser and company data
# python app/create_superuser.py < /dev/null || true
# python app/syncdata.py || true

exec "$@"
