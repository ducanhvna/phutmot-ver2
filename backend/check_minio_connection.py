import os
from minio import Minio
from minio.error import S3Error
from urllib.parse import urlparse, urlunparse

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "etl-data")

if __name__ == "__main__":
    try:
        client = Minio(
            MINIO_ENDPOINT,
            MINIO_ACCESS_KEY,
            MINIO_SECRET_KEY,
            secure=False
        )
        # Kiểm tra bucket
        if not client.bucket_exists(MINIO_BUCKET):
            client.make_bucket(MINIO_BUCKET)
        print(f"[OK] Bucket '{MINIO_BUCKET}' đã sẵn sàng.")
        # Tạo file test
        test_file = "/tmp/minio_test_upload.txt"
        with open(test_file, "w") as f:
            f.write("Hello MinIO!\n")
        object_name = "minio_test_upload.txt"
        client.fput_object(MINIO_BUCKET, object_name, test_file)
        print(f"[OK] Đã upload file '{object_name}' lên bucket '{MINIO_BUCKET}'.")
        # Link public (truy cập trực tiếp trên trình duyệt, không cần đăng nhập)
        public_host = os.getenv("MINIO_PUBLIC_HOST", "localhost")
        # Link port 9000 (API S3 - luôn force download nếu bucket public-read)
        public_url_9000 = f"http://{public_host}:9000/{MINIO_BUCKET}/{object_name}?response-content-disposition=attachment"
        print(f"[OK] Link download trực tiếp (port 9000, luôn tải về): {public_url_9000}")
        # Link port 9001 (UI/gateway, có thể không force download tuỳ cấu hình)
        public_port = os.getenv("MINIO_PUBLIC_PORT", "9001")
        public_url_9001 = f"http://{public_host}:{public_port}/{MINIO_BUCKET}/{object_name}?response-content-disposition=attachment"
        print(f"[OK] Link download trực tiếp (port 9001, UI/gateway): {public_url_9001}")
        # Kiểm tra/cấu hình bucket policy public-read nếu cần
        try:
            policy = client.get_bucket_policy(MINIO_BUCKET)
            if '"Effect":"Allow"' not in policy or '"Principal":"*"' not in policy:
                raise Exception('Bucket policy chưa phải public-read')
            print(f"[OK] Bucket policy đã là public-read.")
        except Exception:
            # Thiết lập policy public-read nếu chưa có
            public_policy = f'''{{
                "Version": "2012-10-17",
                "Statement": [
                    {{
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": ["s3:GetObject"],
                        "Resource": ["arn:aws:s3:::{MINIO_BUCKET}/*"]
                    }}
                ]
            }}'''
            client.set_bucket_policy(MINIO_BUCKET, public_policy)
            print(f"[OK] Đã thiết lập bucket policy public-read cho '{MINIO_BUCKET}'.")
    except S3Error as e:
        print(f"[ERROR] Lỗi MinIO: {e}")
    except Exception as ex:
        print(f"[ERROR] Không thể kết nối MinIO: {ex}")
