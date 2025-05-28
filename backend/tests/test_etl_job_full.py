import pytest
from app.utils.etl_odoo_to_minio import etl_job
import os

def test_etl_job_full_real_services():
    """
    Test the full ETL job with real Odoo and MinIO services.
    This will run extract_from_odoo_and_save_to_minio and load_to_minio with real data.
    The test will pass if the ETL job completes successfully and returns True.
    Ngoài ra, ghi file kết quả ra thư mục test_result để kiểm tra thủ công.
    """
    # Set up environment variables for MinIO if needed
    os.environ["MINIO_ENDPOINT"] = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    os.environ["MINIO_ACCESS_KEY"] = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    os.environ["MINIO_SECRET_KEY"] = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    os.environ["MINIO_BUCKET"] = os.getenv("MINIO_BUCKET", "etl-data")
    # Use a recent date range for real data
    from datetime import datetime, timedelta
    import pandas as pd
    # enddate = datetime.now().strftime("%Y-%m-%d")
    # startdate = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    startdate = "2025-04-01"
    enddate = "2025-04-30"
    # Chạy ETL và lấy kết quả
    from app.utils import etl_odoo_to_minio
    raw_data, raw_url = etl_odoo_to_minio.extract_from_odoo_and_save_to_minio(startdate=startdate, enddate=enddate)
    clean_data = etl_odoo_to_minio.transform(raw_data)
    report_url = etl_odoo_to_minio.load_to_minio(clean_data, f"hrms_etl_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    # Ghi file kết quả ra test_result
    test_result_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../test_result'))
    if not os.path.exists(test_result_dir):
        os.makedirs(test_result_dir)
    # Ghi các link file báo cáo ra Excel
    if isinstance(report_url, dict):
        df_links = pd.DataFrame(list(report_url.items()), columns=["file", "url"])
        df_links.to_excel(os.path.join(test_result_dir, "etl_report_links.xlsx"), index=False)
    # Ghi raw_url ra file txt
    with open(os.path.join(test_result_dir, "etl_raw_url.txt"), "w", encoding="utf-8") as f:
        f.write(str(raw_url))
    # Ghi 1 sheet dữ liệu mẫu (ví dụ employees) ra Excel để kiểm tra
    if "employees" in clean_data:
        clean_data["employees"].to_excel(os.path.join(test_result_dir, "etl_employees.xlsx"), index=False)
    # Ghi toàn bộ clean_data ra một file Excel nhiều sheet
    clean_data_path = os.path.join(test_result_dir, "etl_clean_data_full.xlsx")
    with pd.ExcelWriter(clean_data_path) as writer:
        for key, df in clean_data.items():
            if hasattr(df, 'to_excel'):
                df.to_excel(writer, sheet_name=key[:31], index=False)
    assert isinstance(report_url, dict) and len(report_url) > 0

def test_etl_extract_errors():
    """
    Test kiểm tra lỗi extract: các field không tồn tại, lỗi truy vấn model, ...
    Ghi file extract_errors ra test_result để kiểm tra thủ công.
    """
    from app.utils import etl_odoo_to_minio
    import pandas as pd
    import os
    from datetime import datetime
    startdate = "2025-04-01"
    enddate = "2025-04-30"
    raw_data, _ = etl_odoo_to_minio.extract_from_odoo_and_save_to_minio(startdate=startdate, enddate=enddate)
    extract_errors = raw_data.get('extract_errors', [])
    test_result_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../test_result'))
    if not os.path.exists(test_result_dir):
        os.makedirs(test_result_dir)
    if extract_errors:
        df_err = pd.DataFrame(extract_errors)
        df_err.to_excel(os.path.join(test_result_dir, "etl_extract_errors.xlsx"), index=False)
    # Kiểm tra không có lỗi nghiêm trọng (status == 'lỗi' là fail)
    serious_errors = [e for e in extract_errors if e.get('status') == 'lỗi']
    assert not serious_errors, f"Có lỗi nghiêm trọng khi extract: {serious_errors}"
