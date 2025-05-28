import pytest
from app.utils import etl_odoo_to_minio
import json


# def test_extract_from_odoo_and_save_to_minio(monkeypatch):
    # Patch các extract function để trả về dữ liệu giả
    # monkeypatch.setattr(etl_odoo_to_minio, 'extract_employees', lambda *a, **k: [{"id": 1}])
    # monkeypatch.setattr(etl_odoo_to_minio, 'extract_contracts', lambda *a, **k: [])
    # monkeypatch.setattr(etl_odoo_to_minio, 'extract_companies', lambda *a, **k: [])
    # monkeypatch.setattr(etl_odoo_to_minio, 'extract_leaves', lambda *a, **k: [])
    # monkeypatch.setattr(etl_odoo_to_minio, 'extract_attendance', lambda *a, **k: [])
    # monkeypatch.setattr(etl_odoo_to_minio, 'extract_upload_attendance', lambda *a, **k: [])
    # monkeypatch.setattr(etl_odoo_to_minio, 'extract_kpi_weekly_report_summary', lambda *a, **k: [])
    # monkeypatch.setattr(etl_odoo_to_minio, 'extract_hr_weekly_report', lambda *a, **k: [])
    # monkeypatch.setattr(etl_odoo_to_minio, 'extract_al_report', lambda *a, **k: [])
    # monkeypatch.setattr(etl_odoo_to_minio, 'extract_cl_report', lambda *a, **k: [])
    # Patch xmlrpc only, dùng MinIO thật
    # import types
    # class DummyCommon:
    #     def authenticate(self, *a, **k): return 1
    # class DummyModels:
    #     def execute_kw(self, *a, **k): return []
    # monkeypatch.setattr(etl_odoo_to_minio.xmlrpc.client, 'ServerProxy', lambda url: DummyCommon() if "common" in url else DummyModels())
    # Test


def test_extract_from_odoo_and_save_to_minio():
    # Test trực tiếp, không mock extract_*
    data, url = etl_odoo_to_minio.extract_from_odoo_and_save_to_minio(startdate="2024-05-01", enddate="2024-05-30")
    # Ghi file json và các file excel đầu ra vào thư mục test_result
    import requests, os
    out_dir = "test_result"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    with open(os.path.join(out_dir, "test_etl_result.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    assert "employees" in data
    assert isinstance(url, str) and url.startswith("http")
    # Kiểm tra file thực sự tồn tại trên MinIO
    from minio import Minio
    from urllib.parse import urlparse
    minio_client = Minio(
        os.getenv("MINIO_ENDPOINT", "localhost:9000"),
        os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        secure=False
    )
    bucket = os.getenv("MINIO_BUCKET", "etl-data")
    object_name = os.path.basename(urlparse(url).path)
    found = False
    for obj in minio_client.list_objects(bucket):
        if obj.object_name == object_name:
            found = True
            break
    assert found, f"File {object_name} không tồn tại trên MinIO bucket {bucket}"
