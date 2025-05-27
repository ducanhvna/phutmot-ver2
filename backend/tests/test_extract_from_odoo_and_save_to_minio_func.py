import pytest
from app.utils import etl_odoo_to_minio
import json

def test_extract_from_odoo_and_save_to_minio(monkeypatch):
    # Patch các extract function để trả về dữ liệu giả
    # monkeypatch.setattr(etl_odoo_to_minio, 'extract_employees', lambda *a, **k: [{"id": 1}])
    # monkeypatch.setattr(etl_odoo_to_minio, 'extract_contracts', lambda *a, **k: [])
    # monkeypatch.setattr(etl_odoo_to_minio, 'extract_companies', lambda *a, **k: [])
    monkeypatch.setattr(etl_odoo_to_minio, 'extract_leaves', lambda *a, **k: [])
    monkeypatch.setattr(etl_odoo_to_minio, 'extract_attendance', lambda *a, **k: [])
    monkeypatch.setattr(etl_odoo_to_minio, 'extract_upload_attendance', lambda *a, **k: [])
    monkeypatch.setattr(etl_odoo_to_minio, 'extract_kpi_weekly_report_summary', lambda *a, **k: [])
    monkeypatch.setattr(etl_odoo_to_minio, 'extract_hr_weekly_report', lambda *a, **k: [])
    monkeypatch.setattr(etl_odoo_to_minio, 'extract_al_report', lambda *a, **k: [])
    monkeypatch.setattr(etl_odoo_to_minio, 'extract_cl_report', lambda *a, **k: [])
    # Patch xmlrpc only, dùng MinIO thật
    # import types
    # class DummyCommon:
    #     def authenticate(self, *a, **k): return 1
    # class DummyModels:
    #     def execute_kw(self, *a, **k): return []
    # monkeypatch.setattr(etl_odoo_to_minio.xmlrpc.client, 'ServerProxy', lambda url: DummyCommon() if "common" in url else DummyModels())
    # Test
    data, url = etl_odoo_to_minio.extract_from_odoo_and_save_to_minio(startdate="2024-05-01", enddate="2024-05-30")
    # Lưu kết quả ETL ra file để kiểm tra
    with open("test_etl_result.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    assert "employees" in data
    assert isinstance(url, str) and url.startswith("http")
