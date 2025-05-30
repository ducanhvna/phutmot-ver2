import pytest
from app.utils import etl_odoo_to_minio
from minio import Minio
import os

def test_extract_from_odoo_and_save_to_minio_real_odoo_and_minio():
    # Test thực: gọi extract_from_odoo_and_save_to_minio với Odoo và MinIO thật
    from datetime import datetime
    today = datetime.today()
    startdate = today.replace(day=1).strftime('%Y-%m-%d')
    # Lấy ngày cuối tháng
    import calendar
    last_day = calendar.monthrange(today.year, today.month)[1]
    enddate = today.replace(day=last_day).strftime('%Y-%m-%d')
    data, url = etl_odoo_to_minio.extract_from_odoo_and_save_to_minio(startdate=startdate, enddate=enddate)
    assert "employees" in data
    assert isinstance(url, str) and url.startswith("http")
    # Kiểm tra file thực sự tồn tại trên MinIO
    minio_client = Minio(
        "localhost:9000",
        os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        secure=False
    )
    bucket = os.getenv("MINIO_BUCKET", "etl-data")
    # Lấy object name từ url
    from urllib.parse import urlparse
    object_name = os.path.basename(urlparse(url).path)
    found = False
    for obj in minio_client.list_objects(bucket):
        if obj.object_name == object_name:
            found = True
            break
    assert found, f"File {object_name} không tồn tại trên MinIO bucket {bucket}"

def test_transform():
    data = {
        "employees": [
            {"id": 1, "name": "Nguyen Van A"},
            {"id": 2, "name": "Test User"}
        ],
        "contracts": [],
        "companies": [],
        "leaves": [],
        "attendance": [],
        "upload_attendance": [],
        "kpi_weekly_report_summary": [],
        "hr_weekly_report": []
    }
    result = etl_odoo_to_minio.transform(data)
    assert "employees" in result
    df = result["employees"]
    assert df.shape[0] == 1  # Đã loại bỏ user test

def test_transform_full_normalization():
    import pandas as pd
    # Mock input with all keys and various edge cases
    data = {
        "employees": [
            {"id": 1, "name": "Nguyen Van A"},
            {"id": 2, "name": "Test User"},
            {"id": 1, "name": "Nguyen Van A"}  # duplicate
        ],
        "contracts": [
            {"id": 1, "date_start": "2024-05-01", "date_end": "2024-06-01"},
            {"id": 2, "date_start": None, "date_end": "2024-07-01"}
        ],
        "companies": [
            {"id": 1, "name": "C1"}
        ],
        "leaves": [
            {"id": 1, "date_from": "2024-05-01", "date_to": "2024-05-02"},
            {"id": 2, "date_from": None, "date_to": None}
        ],
        "attendance": [
            {"id": 1, "check_in": "2024-05-01T08:00:00", "check_out": "2024-05-01T17:00:00"},
            {"id": 2, "check_in": None, "check_out": None}
        ],
        "upload_attendance": [
            {"id": 1, "url": "http://test.com/file.xlsx"}
        ],
        "kpi_weekly_report_summary": [
            {"employee_code": "E001", "date": "2024-05-01"},
            {"employee_code": "E002", "date": None}
        ],
        "hr_weekly_report": [
            {"employee_code": "E001", "date": "2024-05-01"},
            {"employee_code": "E002", "date": None}
        ]
    }
    result = etl_odoo_to_minio.transform(data)
    # Check all keys
    for key in [
        "employees", "contracts", "companies", "leaves", "attendance",
        "upload_attendance", "kpi_weekly_report_summary", "hr_weekly_report"
    ]:
        assert key in result
        assert isinstance(result[key], pd.DataFrame)
    # Employees: only 1 row, no test user, no duplicate
    df_emp = result["employees"]
    assert df_emp.shape[0] == 1
    assert not df_emp["name"].str.lower().str.contains("test").any()
    # Contracts: date columns are datetime
    df_contracts = result["contracts"]
    assert pd.api.types.is_datetime64_any_dtype(df_contracts["date_start"])
    assert pd.api.types.is_datetime64_any_dtype(df_contracts["date_end"])
    # Leaves: date columns are datetime
    df_leaves = result["leaves"]
    assert pd.api.types.is_datetime64_any_dtype(df_leaves["date_from"])
    assert pd.api.types.is_datetime64_any_dtype(df_leaves["date_to"])
    # Attendance: check_in/check_out are datetime
    df_att = result["attendance"]
    assert pd.api.types.is_datetime64_any_dtype(df_att["check_in"])
    assert pd.api.types.is_datetime64_any_dtype(df_att["check_out"])
    # KPI Weekly: date is datetime
    df_kpi = result["kpi_weekly_report_summary"]
    if not df_kpi.empty:
        assert pd.api.types.is_datetime64_any_dtype(df_kpi["date"])
    # HR Weekly: date is datetime
    df_hr = result["hr_weekly_report"]
    if not df_hr.empty:
        assert pd.api.types.is_datetime64_any_dtype(df_hr["date"])

def test_load_to_minio():
    import pandas as pd
    df = pd.DataFrame([{"id": 1, "name": "Nguyen Van A"}])
    url = etl_odoo_to_minio.load_to_minio({"employees": df}, "test_report")
    assert url.startswith("http://localhost:9000/") or url.startswith("http://minio/")
    # Kiểm tra file thực sự tồn tại trên MinIO
    minio_client = Minio(
        "localhost:9000",
        os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        secure=False
    )
    bucket = os.getenv("MINIO_BUCKET", "etl-data")
    from urllib.parse import urlparse
    object_name = os.path.basename(urlparse(url).path)
    found = False
    for obj in minio_client.list_objects(bucket):
        if obj.object_name == object_name:
            found = True
            break
    assert found, f"File {object_name} không tồn tại trên MinIO bucket {bucket}"

def test_load_to_minio_all_sheets_and_files():
    import pandas as pd
    data = {
        key: pd.DataFrame([{"id": 1, "val": key}]) for key in [
            "employees", "contracts", "companies", "leaves", "attendance",
            "upload_attendance", "kpi_weekly_report_summary", "hr_weekly_report"
        ]
    }
    url = etl_odoo_to_minio.load_to_minio(data, "test_report_full")
    assert url.startswith("http://localhost:9000/") or url.startswith("http://minio/")
    # Kiểm tra file chính và các file sheet tồn tại trên MinIO
    minio_client = Minio(
        "localhost:9000",
        os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        secure=False
    )
    bucket = os.getenv("MINIO_BUCKET", "etl-data")
    from urllib.parse import urlparse
    main_object_name = os.path.basename(urlparse(url).path)
    found_main = False
    for obj in minio_client.list_objects(bucket):
        if obj.object_name == main_object_name:
            found_main = True
            break
    assert found_main, f"File {main_object_name} không tồn tại trên MinIO bucket {bucket}"
    # Kiểm tra các file sheet
    for key in data:
        sheet_file = f"test_report_full_{key}.xlsx"
        found_sheet = False
        for obj in minio_client.list_objects(bucket):
            if obj.object_name == sheet_file:
                found_sheet = True
                break
        assert found_sheet, f"File {sheet_file} không tồn tại trên MinIO bucket {bucket}"

def test_etl_job(monkeypatch):
    monkeypatch.setattr(etl_odoo_to_minio, 'extract_from_odoo_and_save_to_minio', lambda startdate=None, enddate=None: ("data", "url"))
    monkeypatch.setattr(etl_odoo_to_minio, 'transform', lambda d: d)
    monkeypatch.setattr(etl_odoo_to_minio, 'load_to_minio', lambda d, n: "url")
    assert etl_odoo_to_minio.etl_job(startdate='2025-04-01', enddate='2025-04-03') is True

def test_extract_with_date_filter(monkeypatch):
    # Fake extract_employees để kiểm tra domain truyền xuống
    called = {}
    def fake_extract_employees(models, uid, limit, offset=0, startdate=None, enddate=None):
        called['startdate'] = startdate
        called['enddate'] = enddate
        return []
    monkeypatch.setattr(etl_odoo_to_minio, 'extract_employees', fake_extract_employees)
    # Các extract khác trả về rỗng
    monkeypatch.setattr(etl_odoo_to_minio, 'extract_contracts', lambda *a, **k: [])
    monkeypatch.setattr(etl_odoo_to_minio, 'extract_companies', lambda *a, **k: [])
    monkeypatch.setattr(etl_odoo_to_minio, 'extract_leaves', lambda *a, **k: [])
    monkeypatch.setattr(etl_odoo_to_minio, 'extract_attendance', lambda *a, **k: [])
    monkeypatch.setattr(etl_odoo_to_minio, 'extract_upload_attendance', lambda *a, **k: [])
    monkeypatch.setattr(etl_odoo_to_minio, 'extract_kpi_weekly_report_summary', lambda *a, **k: [])
    monkeypatch.setattr(etl_odoo_to_minio, 'extract_hr_weekly_report', lambda *a, **k: [])
    # Patch xmlrpc
    import types
    class FakeCommon:
        def authenticate(self, *a, **k): return 1
    class FakeModels:
        def execute_kw(self, *a, **k): return []
    fake_xmlrpc = types.SimpleNamespace(
        client=types.SimpleNamespace(
            ServerProxy=lambda url: FakeCommon() if "common" in url else FakeModels()
        )
    )
    monkeypatch.setattr(etl_odoo_to_minio, 'xmlrpc', fake_xmlrpc)
    # Gọi extract_from_odoo_and_save_to_minio với filter ngày (dùng Minio thật)
    data, url = etl_odoo_to_minio.extract_from_odoo_and_save_to_minio(startdate='2025-04-01', enddate='2025-04-03')
    assert called['startdate'] == '2025-04-01'
    assert called['enddate'] == '2025-04-03'

def test_etl_job_with_date(monkeypatch):
    monkeypatch.setattr(etl_odoo_to_minio, 'extract_from_odoo_and_save_to_minio', lambda startdate=None, enddate=None: ("data", "url"))
    monkeypatch.setattr(etl_odoo_to_minio, 'transform', lambda d: d)
    monkeypatch.setattr(etl_odoo_to_minio, 'load_to_minio', lambda d, n: "url")
    # Sử dụng ngày giả định cho test
    result = etl_odoo_to_minio.transform(data, startdate="2024-01-01", enddate="2024-12-31")
    assert etl_odoo_to_minio.etl_job(startdate='2025-04-01', enddate='2025-04-03') is True
