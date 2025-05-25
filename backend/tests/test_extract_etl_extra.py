import pytest
from app.utils import etl_odoo_to_minio

def test_extract_upload_attendance(monkeypatch):
    class FakeModels:
        def execute_kw(self, db, uid, pwd, model, method, args, kwargs):
            assert model == 'hr.upload.attendance'
            assert method == 'search_read'
            return [
                {'id': 1, 'year': 2024, 'month': 5, 'template': 1, 'company_id': 1, 'department_id': 2, 'url': 'http://test.com/file.xlsx'}
            ]
    fake_models = FakeModels()
    res = etl_odoo_to_minio.extract_upload_attendance(fake_models, 1, 10, 0)
    assert isinstance(res, list)
    assert res[0]['id'] == 1

def test_extract_kpi_weekly_report_summary(monkeypatch):
    class FakeModels:
        def execute_kw(self, db, uid, pwd, model, method, args, kwargs):
            assert model == 'kpi.weekly.report.summary'
            assert method == 'search_read'
            return [
                {'employee_code': 'E001', 'date': '2024-05-01', 'employee_name': 'A', 'company_name': 'C', 'department_name': 'D', 'employee_level': 'L',
                 'compensation_amount_week_1': 1, 'compensation_amount_week_2': 2, 'compensation_amount_week_3': 3, 'compensation_amount_week_4': 4, 'compensation_amount_week_5': 5,
                 'compensation_status_week_1': 'ok', 'compensation_status_week_2': 'ok', 'compensation_status_week_3': 'ok', 'compensation_status_week_4': 'ok', 'compensation_status_week_5': 'ok',
                 'book_review_compensation_status': 'done'}
            ]
    fake_models = FakeModels()
    res = etl_odoo_to_minio.extract_kpi_weekly_report_summary(fake_models, 1, 10, 0)
    assert isinstance(res, list)
    assert res[0]['employee_code'] == 'E001'

def test_extract_hr_weekly_report(monkeypatch):
    class FakeModels:
        def execute_kw(self, db, uid, pwd, model, method, args, kwargs):
            assert model == 'hr.weekly.report'
            assert method == 'search_read'
            return [
                {'employee_code': 'E001', 'department_id': 1, 'employee_id': 2, 'company_id': 3, 'create_date': '2024-05-01',
                 'job_title': 'Dev', 'date': '2024-05-01', 'state': 'done', 'from_date': '2024-05-01', 'to_date': '2024-05-07'}
            ]
    fake_models = FakeModels()
    res = etl_odoo_to_minio.extract_hr_weekly_report(fake_models, 1, 10, 0)
    assert isinstance(res, list)
    assert res[0]['employee_code'] == 'E001'
