#!/bin/sh
set -e

# Start MinIO server in background
you_can_run="/usr/bin/minio"
if [ ! -x "$you_can_run" ]; then
  you_can_run="minio"
fi
$you_can_run server --console-address ":9001" /data &

# Wait for MinIO to be ready
sleep 5

# Download mc (MinIO Client) if not present
if ! command -v mc >/dev/null 2>&1; then
  wget -qO /usr/bin/mc https://dl.min.io/client/mc/release/linux-amd64/mc && chmod +x /usr/bin/mc
fi

# Configure mc and create bucket
mc alias set myminio http://localhost:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"
mc mb -p myminio/etl-data || true

# Wait for background MinIO process
wait
