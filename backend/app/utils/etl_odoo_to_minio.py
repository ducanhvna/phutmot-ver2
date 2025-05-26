import os
import xmlrpc.client
import pandas as pd
from minio import Minio
from datetime import datetime
import tempfile

ODOO_BASE_URL = "https://hrm.mandalahotel.com.vn"
ODOO_DB = "apechrm_product_v3"
ODOO_USERNAME = "admin_ho"
ODOO_PASSWORD = "43a824d3a724da2b59d059d909f13ba0c38fcb82"

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "etl-data")

# 1. Extract
def extract_employees(models, uid, limit, offset=0, startdate=None, enddate=None):
    fields = ['id', 'name', 'user_id', 'employee_ho', 'part_time_company_id', 'part_time_department_id',
                'company_id', 'code', 'department_id', 'time_keeping_code', 'job_title',
                'probationary_contract_termination_date', 'severance_day', 'workingday',
                'probationary_salary_rate', 'resource_calendar_id', 'date_sign', 'level']
    domain = []
    if startdate and enddate:
        domain = ['&', ('create_date', '>=', startdate), ('create_date', '<=', enddate)]
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.employee', 'search_read', [domain, fields], {'limit': limit, 'offset': offset})

def extract_contracts(models, uid, limit, offset=0, startdate=None, enddate=None):
    fields = [
        'id', 'name', 'employee_id', 'date_start', 'date_end', 'wage', 'state',
        'minutes_per_day', 'employee_code', 'resource_calendar_id'
    ]
    domain = []
    if startdate and enddate:
        domain = ['&', ('date_start', '>=', startdate), ('date_start', '<=', enddate)]
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.contract', 'search_read', [domain, fields], {'limit': limit, 'offset': offset})

def extract_companies(models, uid, limit, offset=0):
    fields = ['id', 'name', 'partner_id', 'email', 'phone', 'is_ho', 'mis_id']
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.company', 'search_read', [[], fields], {'limit': limit, 'offset': offset})

def extract_leaves(models, uid, limit, offset=0, startdate=None, enddate=None):
    fields = ['id', 'name', 'employee_id', 'holiday_status_id', 'date_from', 'date_to', 'state']
    domain = []
    if startdate and enddate:
        domain = ['&', ('date_from', '>=', startdate), ('date_from', '<=', enddate)]
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.leave', 'search_read', [domain, fields], {'limit': limit, 'offset': offset})

def extract_attendance(models, uid, limit, offset=0, startdate=None, enddate=None):
    fields = ['id', 'employee_id', 'check_in', 'check_out', 'worked_hours']
    domain = []
    if startdate and enddate:
        domain = ['&', ('check_in', '>=', startdate), ('check_in', '<=', enddate)]
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.attendance', 'search_read', [domain, fields], {'limit': limit, 'offset': offset})

def extract_upload_attendance(models, uid, limit, offset=0, startdate=None, enddate=None):
    fields = ['id', 'year', 'month', 'template', 'company_id', 'department_id', 'url']
    domain = []
    if startdate and enddate:
        # Giả sử filter theo year/month nếu có, hoặc bỏ qua nếu không phù hợp
        pass
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.upload.attendance', 'search_read', [domain, fields], {'limit': limit, 'offset': offset})

def extract_kpi_weekly_report_summary(models, uid, limit, offset=0, startdate=None, enddate=None):
    fields = [
        'employee_code', 'date', 'employee_name', 'company_name', 'department_name', 'employee_level',
        'compensation_amount_week_1', 'compensation_amount_week_2', 'compensation_amount_week_3',
        'compensation_amount_week_4', 'compensation_amount_week_5',
        'compensation_status_week_1', 'compensation_status_week_2', 'compensation_status_week_3',
        'compensation_status_week_4', 'compensation_status_week_5', 'book_review_compensation_status'
    ]
    domain = []
    if startdate and enddate:
        domain = ['&', ('date', '>=', startdate), ('date', '<=', enddate)]
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'kpi.weekly.report.summary', 'search_read', [domain, fields], {'limit': limit, 'offset': offset})

def extract_hr_weekly_report(models, uid, limit, offset=0, startdate=None, enddate=None):
    fields = [
        'employee_code', 'department_id', 'employee_id', 'company_id', 'create_date',
        'job_title', 'date', 'state', 'from_date', 'to_date'
    ]
    domain = []
    if startdate and enddate:
        domain = ['&', ('date', '>=', startdate), ('date', '<=', enddate)]
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.weekly.report', 'search_read', [domain, fields], {'limit': limit, 'offset': offset})

# 1. Extract tổng hợp với phân trang

def extract_from_odoo_and_save_to_minio(pagesize=100, startdate=None, enddate=None):
    if not startdate or not enddate:
        raise ValueError("startdate và enddate là bắt buộc nhập")
    common = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/object")
    # Phân trang lấy dữ liệu
    def fetch_all(extract_func, **kwargs):
        all_data = []
        offset = 0
        while True:
            batch = extract_func(models, uid, pagesize, offset, **kwargs)
            if not batch:
                break
            all_data.extend(batch)
            if len(batch) < pagesize:
                break
            offset += pagesize
        return all_data
    employees = fetch_all(extract_employees, startdate=startdate, enddate=enddate)
    contracts = fetch_all(extract_contracts, startdate=startdate, enddate=enddate)
    companies = fetch_all(extract_companies)  # Không filter ngày
    leaves = fetch_all(extract_leaves, startdate=startdate, enddate=enddate)
    attendance = fetch_all(extract_attendance, startdate=startdate, enddate=enddate)
    upload_attendance = fetch_all(extract_upload_attendance, startdate=startdate, enddate=enddate)
    kpi_weekly_report_summary = fetch_all(extract_kpi_weekly_report_summary, startdate=startdate, enddate=enddate)
    hr_weekly_report = fetch_all(extract_hr_weekly_report, startdate=startdate, enddate=enddate)
    data = {
        "employees": employees,
        "contracts": contracts,
        "companies": companies,
        "leaves": leaves,
        "attendance": attendance,
        "upload_attendance": upload_attendance,
        "kpi_weekly_report_summary": kpi_weekly_report_summary,
        "hr_weekly_report": hr_weekly_report,
    }
    # Save raw data to Excel and upload to MinIO
    client = Minio(MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, secure=False)
    # Luôn tạo bucket nếu chưa có (xử lý race condition)
    try:
        if not client.bucket_exists(MINIO_BUCKET):
            client.make_bucket(MINIO_BUCKET)
    except Exception:
        pass  # Nếu bucket đã tồn tại do race condition, bỏ qua lỗi
    # Sử dụng thư mục tạm hợp lệ trên mọi hệ điều hành
    tmp_dir = tempfile.gettempdir()
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir, exist_ok=True)
    file_path = os.path.join(tmp_dir, f"odoo_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    with pd.ExcelWriter(file_path) as writer:
        for key, value in data.items():
            df = pd.DataFrame(value)
            df.to_excel(writer, sheet_name=key, index=False)
    object_name = os.path.basename(file_path)
    # Đảm bảo file thực sự được upload lên MinIO
    client.fput_object(MINIO_BUCKET, object_name, file_path)
    # Kiểm tra lại object vừa upload
    found = False
    for obj in client.list_objects(MINIO_BUCKET, prefix=object_name):
        if obj.object_name == object_name:
            found = True
            break
    if not found:
        raise RuntimeError(f"File {object_name} was not uploaded to MinIO bucket {MINIO_BUCKET}")
    url = client.presigned_get_object(MINIO_BUCKET, object_name)
    return data, url

# 2. Transform
def transform(data):
    # Chuẩn hóa, loại bỏ test, merge dữ liệu, tính toán tổng hợp
    result = {}
    # Employees
    df_emp = pd.DataFrame(data["employees"])
    if not df_emp.empty:
        df_emp = df_emp.drop_duplicates(subset=["id"])
        df_emp = df_emp[~df_emp["name"].str.lower().str.contains("test")]
    result["employees"] = df_emp
    # Contracts
    df_contracts = pd.DataFrame(data["contracts"])
    if not df_contracts.empty:
        df_contracts["date_start"] = pd.to_datetime(df_contracts["date_start"], errors="coerce")
        df_contracts["date_end"] = pd.to_datetime(df_contracts["date_end"], errors="coerce")
    result["contracts"] = df_contracts
    # Companies
    df_companies = pd.DataFrame(data["companies"])
    result["companies"] = df_companies
    # Leaves
    df_leaves = pd.DataFrame(data["leaves"])
    if not df_leaves.empty:
        df_leaves["date_from"] = pd.to_datetime(df_leaves["date_from"], errors="coerce")
        df_leaves["date_to"] = pd.to_datetime(df_leaves["date_to"], errors="coerce")
    result["leaves"] = df_leaves
    # Attendance
    df_attendance = pd.DataFrame(data["attendance"])
    if not df_attendance.empty:
        df_attendance["check_in"] = pd.to_datetime(df_attendance["check_in"], errors="coerce")
        df_attendance["check_out"] = pd.to_datetime(df_attendance["check_out"], errors="coerce")
    result["attendance"] = df_attendance
    # Upload Attendance
    df_upload_attendance = pd.DataFrame(data["upload_attendance"])
    result["upload_attendance"] = df_upload_attendance
    # KPI Weekly Report Summary
    df_kpi_weekly = pd.DataFrame(data["kpi_weekly_report_summary"])
    if not df_kpi_weekly.empty and "date" in df_kpi_weekly:
        df_kpi_weekly["date"] = pd.to_datetime(df_kpi_weekly["date"], errors="coerce")
    result["kpi_weekly_report_summary"] = df_kpi_weekly
    # HR Weekly Report
    df_hr_weekly = pd.DataFrame(data["hr_weekly_report"])
    if not df_hr_weekly.empty and "date" in df_hr_weekly:
        df_hr_weekly["date"] = pd.to_datetime(df_hr_weekly["date"], errors="coerce")
    result["hr_weekly_report"] = df_hr_weekly
    # Có thể bổ sung merge, join, tính toán tổng hợp ở đây nếu cần
    return result

# 3. Load to MinIO (public-read, truy cập qua port 9000 sẽ tải về trực tiếp)
def load_to_minio(data, report_name):
    client = Minio(MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, secure=False)
    # Đảm bảo bucket tồn tại
    if not client.bucket_exists(MINIO_BUCKET):
        client.make_bucket(MINIO_BUCKET)
    # Đảm bảo bucket policy là public-read
    try:
        policy = client.get_bucket_policy(MINIO_BUCKET)
        if '"Effect":"Allow"' not in policy or '"Principal":"*"' not in policy:
            raise Exception('Bucket policy chưa phải public-read')
    except Exception:
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
    # Lưu nhiều file báo cáo excel (mỗi sheet 1 loại dữ liệu)
    tmp_dir = tempfile.gettempdir()
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir, exist_ok=True)
    file_path = os.path.join(tmp_dir, f"{report_name}.xlsx")
    with pd.ExcelWriter(file_path) as writer:
        for key, df in data.items():
            if isinstance(df, pd.DataFrame):
                df.to_excel(writer, sheet_name=key[:31], index=False)
    client.fput_object(MINIO_BUCKET, f"{report_name}.xlsx", file_path)
    # Ngoài file tổng hợp, xuất thêm từng file nhỏ nếu cần
    for key, df in data.items():
        if isinstance(df, pd.DataFrame) and not df.empty:
            sub_file = os.path.join(tmp_dir, f"{report_name}_{key}.xlsx")
            df.to_excel(sub_file, index=False)
            client.fput_object(MINIO_BUCKET, f"{report_name}_{key}.xlsx", sub_file)
    # Trả về link public tải về qua port 9000 và 9001
    public_host = os.getenv("MINIO_PUBLIC_HOST", "localhost")
    public_url_9000 = f"http://{public_host}:9000/{MINIO_BUCKET}/{report_name}.xlsx?response-content-disposition=attachment"
    public_port = os.getenv("MINIO_PUBLIC_PORT", "9001")
    public_url_9001 = f"http://{public_host}:{public_port}/{MINIO_BUCKET}/{report_name}.xlsx?response-content-disposition=attachment"
    print(f"[ETL] Link download trực tiếp (port 9000, luôn tải về): {public_url_9000}")
    print(f"[ETL] Link download trực tiếp (port 9001, UI/gateway): {public_url_9001}")
    return public_url_9000

# 4. ETL Job
def etl_job(startdate=None, enddate=None):
    try:
        raw_data, raw_url = extract_from_odoo_and_save_to_minio(startdate=startdate, enddate=enddate)
        clean_data = transform(raw_data)
        report_url = load_to_minio(clean_data, f"hrms_etl_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        print(f"[ETL] Success. Raw: {raw_url} | Report: {report_url}")
        return True
    except Exception as e:
        print(f"[ETL] Failed: {e}")
        return False

if __name__ == "__main__":
    etl_job()
