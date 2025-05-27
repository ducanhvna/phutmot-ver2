from app.utils import etl_odoo_to_minio

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
