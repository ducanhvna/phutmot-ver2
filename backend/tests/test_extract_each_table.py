import pytest
from app.utils import etl_odoo_to_minio

def test_extract_employees():
    data, _ = etl_odoo_to_minio.extract_from_odoo_and_save_to_minio(pagesize=10, startdate="2024-01-01", enddate="2024-12-31")
    assert isinstance(data["employees"], list)
    print(f"employees: {len(data['employees'])}")

def test_extract_contracts():
    data, _ = etl_odoo_to_minio.extract_from_odoo_and_save_to_minio(pagesize=10, startdate="2024-01-01", enddate="2024-12-31")
    assert isinstance(data["contracts"], list)
    print(f"contracts: {len(data['contracts'])}")

def test_extract_companies():
    data, _ = etl_odoo_to_minio.extract_from_odoo_and_save_to_minio(pagesize=10, startdate="2024-01-01", enddate="2024-12-31")
    assert isinstance(data["companies"], list)
    print(f"companies: {len(data['companies'])}")

def test_extract_leaves():
    data, _ = etl_odoo_to_minio.extract_from_odoo_and_save_to_minio(pagesize=10, startdate="2024-01-01", enddate="2024-12-31")
    assert isinstance(data["leaves"], list)
    print(f"leaves: {len(data['leaves'])}")

def test_extract_attendance():
    data, _ = etl_odoo_to_minio.extract_from_odoo_and_save_to_minio(pagesize=10, startdate="2024-01-01", enddate="2024-12-31")
    assert isinstance(data["attendance"], list)
    print(f"attendance: {len(data['attendance'])}")

def test_extract_upload_attendance():
    data, _ = etl_odoo_to_minio.extract_from_odoo_and_save_to_minio(pagesize=10, startdate="2024-01-01", enddate="2024-12-31")
    assert isinstance(data["upload_attendance"], list)
    print(f"upload_attendance: {len(data['upload_attendance'])}")

def test_extract_kpi_weekly_report_summary():
    data, _ = etl_odoo_to_minio.extract_from_odoo_and_save_to_minio(pagesize=10, startdate="2024-01-01", enddate="2024-12-31")
    assert isinstance(data["kpi_weekly_report_summary"], list)
    print(f"kpi_weekly_report_summary: {len(data['kpi_weekly_report_summary'])}")

def test_extract_hr_weekly_report():
    data, _ = etl_odoo_to_minio.extract_from_odoo_and_save_to_minio(pagesize=10, startdate="2024-01-01", enddate="2024-12-31")
    assert isinstance(data["hr_weekly_report"], list)
    print(f"hr_weekly_report: {len(data['hr_weekly_report'])}")

def test_extract_al_report():
    data, _ = etl_odoo_to_minio.extract_from_odoo_and_save_to_minio(pagesize=10, startdate="2024-01-01", enddate="2024-12-31")
    assert isinstance(data["al_report"], list)
    print(f"al_report: {len(data['al_report'])}")

def test_extract_cl_report():
    data, _ = etl_odoo_to_minio.extract_from_odoo_and_save_to_minio(pagesize=10, startdate="2024-01-01", enddate="2024-12-31")
    assert isinstance(data["cl_report"], list)
    print(f"cl_report: {len(data['cl_report'])}")
