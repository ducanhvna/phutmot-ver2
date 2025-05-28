import os
import xmlrpc.client
import pandas as pd
from minio import Minio
from datetime import datetime
import tempfile
from .report_exporters import (
    export_al_cl_report_department,
    export_sumary_attendance_report,
    export_sumary_attendance_report_department,
    export_late_in_5_miniutes_report_ho,
    export_feed_report,
    export_kpi_weekly_report_ho,
    export_kpi_weekly_report,
    export_al_cl_report_ho,
    export_al_cl_report,
    export_al_cl_report_severance,
)

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

ODOO_BASE_URL = "https://hrm.mandalahotel.com.vn"
ODOO_DB = "apechrm_product_v3"
ODOO_USERNAME = "admin_ho"
ODOO_PASSWORD = "43a824d3a724da2b59d059d909f13ba0c38fcb82"

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "etl-data")

# 1. Extract
def extract_employees(models, uid, limit, offset=0, startdate=None, enddate=None, fields=None):
    default_fields = ['id', 'name', 'user_id', 'employee_ho', 'part_time_company_id', 'part_time_department_id',
                'company_id', 'code', 'department_id', 'time_keeping_code', 'job_title',
                'probationary_contract_termination_date', 'severance_day', 'workingday',
                'probationary_salary_rate', 'resource_calendar_id', 'date_sign', 'level']
    fields = fields or default_fields
    if startdate and enddate:
        domain = ["&", ("create_date", ">=", startdate), ("create_date", "<=", enddate)]
    else:
        domain = []
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.employee', 'search_read', [domain, fields], {'limit': limit, 'offset': offset})

def extract_contracts(models, uid, limit, offset=0, startdate=None, enddate=None, fields=None):
    default_fields = [
        'id', 'name', 'employee_id', 'date_start', 'date_end', 'wage', 'state',
        'minutes_per_day', 'employee_code', 'resource_calendar_id'
    ]
    fields = fields or default_fields
    if startdate and enddate:
        domain = ["&", ("date_start", ">=", startdate), ("date_start", "<=", enddate)]
    else:
        domain = []
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.contract', 'search_read', [domain, fields], {'limit': limit, 'offset': offset})

def extract_companies(models, uid, limit, offset=0, fields=None):
    default_fields = ['id', 'name', 'partner_id', 'email', 'phone', 'is_ho', 'mis_id']
    fields = fields or default_fields
    domain = []
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.company', 'search_read', [domain, fields], {'limit': limit, 'offset': offset})

def extract_leaves(models, uid, limit, offset=0, startdate=None, enddate=None, fields=None):
    default_fields = ['id', 'name', 'employee_id', 'holiday_status_id', 'date_from', 'date_to', 'state']
    fields = fields or default_fields
    if startdate and enddate:
        domain = ["&", ("date_from", ">=", startdate), ("date_from", "<=", enddate)]
    else:
        domain = []
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.leave', 'search_read', [domain, fields], {'limit': limit, 'offset': offset})

def extract_attendance(models, uid, limit, offset=0, startdate=None, enddate=None, fields=None):
    default_fields = ['id', 'employee_id', 'check_in', 'check_out', 'worked_hours']
    fields = fields or default_fields
    if startdate and enddate:
        domain = ["&", ("check_in", ">=", startdate), ("check_in", "<=", enddate)]
    else:
        domain = []
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.attendance', 'search_read', [domain, fields], {'limit': limit, 'offset': offset})

def extract_upload_attendance(models, uid, limit, offset=0, startdate=None, enddate=None, fields=None):
    default_fields = ['id', 'year', 'month', 'template', 'company_id', 'department_id', 'url']
    fields = fields or default_fields
    domain = []
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.upload.attendance', 'search_read', [domain, fields], {'limit': limit, 'offset': offset})

def extract_kpi_weekly_report_summary(models, uid, limit, offset=0, startdate=None, enddate=None, fields=None):
    default_fields = [
        'employee_code', 'date', 'employee_name', 'company_name', 'department_name', 'employee_level',
        'compensation_amount_week_1', 'compensation_amount_week_2', 'compensation_amount_week_3',
        'compensation_amount_week_4', 'compensation_amount_week_5',
        'compensation_status_week_1', 'compensation_status_week_2', 'compensation_status_week_3',
        'compensation_status_week_4', 'compensation_status_week_5', 'book_review_compensation_status'
    ]
    fields = fields or default_fields
    if startdate and enddate:
        domain = ["&", ("date", ">=", startdate), ("date", "<=", enddate)]
    else:
        domain = []
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'kpi.weekly.report.summary', 'search_read', [domain, fields], {'limit': limit, 'offset': offset})

def extract_hr_weekly_report(models, uid, limit, offset=0, startdate=None, enddate=None, fields=None):
    default_fields = [
        'employee_code', 'department_id', 'employee_id', 'company_id', 'create_date',
        'job_title', 'date', 'state', 'from_date', 'to_date'
    ]
    fields = fields or default_fields
    if startdate and enddate:
        domain = ["&", ("date", ">=", startdate), ("date", "<=", enddate)]
    else:
        domain = []
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.weekly.report', 'search_read', [domain, fields], {'limit': limit, 'offset': offset})

def extract_al_report(models, uid, limit, offset=0, startdate=None, enddate=None, fields=None):
    default_fields = [
        'id','year', 'date_calculate_leave', 'employee_id', 'company_id','employee_code','department_id','standard_day',
        'workingday','date_sign','date_apply_leave','severance_day','seniority_leave', 'job_title', 
        'family_leave','leave_increase_by_seniority_leave','leave_day','leave_year',
        'remaining_leave','january','february','march','april','may','june','july',
        'august','september','october','november','december','leave_used','remaining_leave_minute',
        'remaining_leave_day','note','file','employee_ho','part_time_company_id'
    ]
    fields = fields or default_fields
    if startdate and enddate:
        domain = ["&", ("date_calculate_leave", ">=", startdate), ("date_calculate_leave", "<=", enddate)]
    else:
        domain = []
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.al.report', 'search_read', [domain, fields], {'limit': limit, 'offset': offset})

def extract_cl_report(models, uid, limit, offset=0, startdate=None, enddate=None, fields=None):
    default_fields = [
        'id','year', 'date_calculate', 'employee_id', 'tier','employee_code','department_id','job_title',
        'workingday','date_sign','contract_type_id','severance_day',
        'increase_probationary_1','increase_official_1','used_probationary_1','used_official_1','overtime_probationary_1', 'overtime_official_1',
        'increase_probationary_2','increase_official_2','used_probationary_2','used_official_2','overtime_probationary_2', 'overtime_official_2',
        'increase_probationary_3','increase_official_3','used_probationary_3','used_official_3','overtime_probationary_3', 'overtime_official_3',
        'increase_probationary_4','increase_official_4','used_probationary_4','used_official_4','overtime_probationary_4', 'overtime_official_4',
        'increase_probationary_5','increase_official_5','used_probationary_5','used_official_5','overtime_probationary_5', 'overtime_official_5',
        'increase_probationary_6','increase_official_6','used_probationary_6','used_official_6','overtime_probationary_6', 'overtime_official_6',
        'increase_probationary_7','increase_official_7','used_probationary_7','used_official_7','overtime_probationary_7', 'overtime_official_7',
        'increase_probationary_8','increase_official_8','used_probationary_8','used_official_8','overtime_probationary_8', 'overtime_official_8',
        'increase_probationary_9','increase_official_9','used_probationary_9','used_official_9','overtime_probationary_9', 'overtime_official_9',
        'increase_probationary_10','increase_official_10','used_probationary_10','used_official_10','overtime_probationary_10', 'overtime_official_10',
        'increase_probationary_11','increase_official_11','used_probationary_11','used_official_11','overtime_probationary_11', 'overtime_official_11',
        'increase_probationary_12','increase_official_12','used_probationary_12','used_official_12','overtime_probationary_12', 'overtime_official_12',
        'remaining_total_day', 'remaining_probationary_minute', 'remaining_official_minute', 'remaining_total_minute',
        'company_name', 'company_sid', 'employee_name', 'AUTO-CALCULATE-HOLIDAY', 'NIGHT-HOLIDAY-WAGE'
    ]
    fields = fields or default_fields
    if startdate and enddate:
        domain = ["&", ("date_calculate", ">=", startdate), ("date_calculate", "<=", enddate)]
    else:
        domain = []
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.cl.report', 'search_read', [domain, fields], {'limit': limit, 'offset': offset})

# 1. Extract tổng hợp với phân trang

def extract_from_odoo_and_save_to_minio(pagesize=100, startdate=None, enddate=None):
    if not startdate or not enddate:
        raise ValueError("startdate và enddate là bắt buộc nhập")
    print(f"[ETL] Đang kết nối Odoo: {ODOO_BASE_URL}, DB: {ODOO_DB}, USER: {ODOO_USERNAME}")
    common = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    print(f"[ETL] UID sau khi authenticate: {uid}")
    if not uid:
        raise RuntimeError("Không authenticate được với Odoo. Kiểm tra lại thông tin đăng nhập!")
    models = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/object")
    # Phân trang lấy dữ liệu
    # --- Mapping extract_func -> model_name Odoo ---
    extract_func_to_model = {
        extract_employees: 'hr.employee',
        extract_contracts: 'hr.contract',
        extract_companies: 'res.company',
        extract_leaves: 'hr.leave',
        extract_attendance: 'hr.attendance',
        extract_upload_attendance: 'hr.upload.attendance',
        extract_kpi_weekly_report_summary: 'kpi.weekly.report.summary',
        extract_hr_weekly_report: 'hr.weekly.report',
        extract_al_report: 'hr.al.report',
        extract_cl_report: 'hr.cl.report',
    }
    def fetch_all(extract_func, fields, **kwargs):
        all_data = []
        offset = 0
        # --- Lấy model name và loại bỏ các trường không tồn tại ---
        model_name = extract_func_to_model.get(extract_func)
        if model_name:
            try:
                # Lấy valid fields từ Odoo
                valid_fields = set(models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD, model_name, 'fields_get', [], {}).keys())
                filtered_fields = [f for f in fields if f in valid_fields]
            except Exception as ex:
                print(f"[ETL] Warning: Không kiểm tra được fields cho model {model_name}: {ex}")
                filtered_fields = fields
        else:
            filtered_fields = fields
        while True:
            batch = extract_func(models, uid, 100, offset, fields=filtered_fields, **kwargs)
            print(f"[ETL] {extract_func.__name__} offset={offset} batch_size={len(batch) if batch else 0}")
            if not batch:
                break
            all_data.extend(batch)
            if len(batch) < 100:
                break
            offset += 100
        return all_data
    # Khai báo fields cho từng extract
    employees_fields = ['id', 'name', 'user_id', 'employee_ho', 'part_time_company_id', 'part_time_department_id',
                'company_id', 'code', 'department_id', 'time_keeping_code', 'job_title',
                'probationary_contract_termination_date', 'severance_day', 'workingday',
                'probationary_salary_rate', 'resource_calendar_id', 'date_sign', 'level']
    contracts_fields = [
        'id', 'name', 'employee_id', 'date_start', 'date_end', 'wage', 'state',
        'minutes_per_day', 'employee_code', 'resource_calendar_id'
    ]
    companies_fields = ['id', 'name', 'partner_id', 'email', 'phone', 'is_ho', 'mis_id']
    leaves_fields = ['id', 'name', 'employee_id', 'holiday_status_id', 'date_from', 'date_to', 'state']
    attendance_fields = ['id', 'employee_id', 'check_in', 'check_out', 'worked_hours']
    upload_attendance_fields = ['id', 'year', 'month', 'template', 'company_id', 'department_id', 'url']
    kpi_weekly_report_summary_fields = [
        'employee_code', 'date', 'employee_name', 'company_name', 'department_name', 'employee_level',
        'compensation_amount_week_1', 'compensation_amount_week_2', 'compensation_amount_week_3',
        'compensation_amount_week_4', 'compensation_amount_week_5',
        'compensation_status_week_1', 'compensation_status_week_2', 'compensation_status_week_3',
        'compensation_status_week_4', 'compensation_status_week_5', 'book_review_compensation_status'
    ]
    hr_weekly_report_fields = [
        'employee_code', 'department_id', 'employee_id', 'company_id', 'create_date',
        'job_title', 'date', 'state', 'from_date', 'to_date'
    ]
    al_report_fields = [
        'id','year', 'date_calculate_leave', 'employee_id', 'company_id','employee_code','department_id','standard_day',
        'workingday','date_sign','date_apply_leave','severance_day','seniority_leave', 'job_title', 
        'family_leave','leave_increase_by_seniority_leave','leave_day','leave_year',
        'remaining_leave','january','february','march','april','may','june','july',
        'august','september','october','november','december','leave_used','remaining_leave_minute',
        'remaining_leave_day','note','file','employee_ho','part_time_company_id'
    ]
    cl_report_fields = [
        'id','year', 'date_calculate', 'employee_id', 'tier','employee_code','department_id','job_title',
        'workingday','date_sign','contract_type_id','severance_day',
        'increase_probationary_1','increase_official_1','used_probationary_1','used_official_1','overtime_probationary_1', 'overtime_official_1',
        'increase_probationary_2','increase_official_2','used_probationary_2','used_official_2','overtime_probationary_2', 'overtime_official_2',
        'increase_probationary_3','increase_official_3','used_probationary_3','used_official_3','overtime_probationary_3', 'overtime_official_3',
        'increase_probationary_4','increase_official_4','used_probationary_4','used_official_4','overtime_probationary_4', 'overtime_official_4',
        'increase_probationary_5','increase_official_5','used_probationary_5','used_official_5','overtime_probationary_5', 'overtime_official_5',
        'increase_probationary_6','increase_official_6','used_probationary_6','used_official_6','overtime_probationary_6', 'overtime_official_6',
        'increase_probationary_7','increase_official_7','used_probationary_7','used_official_7','overtime_probationary_7', 'overtime_official_7',
        'increase_probationary_8','increase_official_8','used_probationary_8','used_official_8','overtime_probationary_8', 'overtime_official_8',
        'increase_probationary_9','increase_official_9','used_probationary_9','used_official_9','overtime_probationary_9', 'overtime_official_9',
        'increase_probationary_10','increase_official_10','used_probationary_10','used_official_10','overtime_probationary_10', 'overtime_official_10',
        'increase_probationary_11','increase_official_11','used_probationary_11','used_official_11','overtime_probationary_11', 'overtime_official_11',
        'increase_probationary_12','increase_official_12','used_probationary_12','used_official_12','overtime_probationary_12', 'overtime_official_12',
        'remaining_total_day', 'remaining_probationary_minute', 'remaining_official_minute', 'remaining_total_minute',
        'company_name', 'company_sid', 'employee_name', 'AUTO-CALCULATE-HOLIDAY', 'NIGHT-HOLIDAY-WAGE'
    ]
    # Gọi extract với fields truyền vào
    employees = fetch_all(extract_employees, employees_fields, startdate=startdate, enddate=enddate)
    contracts = fetch_all(extract_contracts, contracts_fields, startdate=startdate, enddate=enddate)
    companies = fetch_all(extract_companies, companies_fields)  # Không filter ngày
    leaves = fetch_all(extract_leaves, leaves_fields, startdate=startdate, enddate=enddate)
    attendance = fetch_all(extract_attendance, attendance_fields, startdate=startdate, enddate=enddate)
    upload_attendance = fetch_all(extract_upload_attendance, upload_attendance_fields, startdate=startdate, enddate=enddate)
    kpi_weekly_report_summary = fetch_all(extract_kpi_weekly_report_summary, kpi_weekly_report_summary_fields, startdate=startdate, enddate=enddate)
    hr_weekly_report = fetch_all(extract_hr_weekly_report, hr_weekly_report_fields, startdate=startdate, enddate=enddate)
    al_report = fetch_all(extract_al_report, al_report_fields, startdate=startdate, enddate=enddate)
    cl_report = fetch_all(extract_cl_report, cl_report_fields, startdate=startdate, enddate=enddate)
    data = {
        "employees": employees,
        "contracts": contracts,
        "companies": companies,
        "leaves": leaves,
        "attendance": attendance,
        "upload_attendance": upload_attendance,
        "kpi_weekly_report_summary": kpi_weekly_report_summary,
        "hr_weekly_report": hr_weekly_report,
        "al_report": al_report,
        "cl_report": cl_report,
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
    # AL Report
    df_al_report = pd.DataFrame(data["al_report"])
    if not df_al_report.empty:
        df_al_report["year"] = pd.to_datetime(df_al_report["year"], format="%Y", errors="coerce")
    result["al_report"] = df_al_report
    # CL Report
    df_cl_report = pd.DataFrame(data["cl_report"])
    if not df_cl_report.empty:
        df_cl_report["year"] = pd.to_datetime(df_cl_report["year"], format="%Y", errors="coerce")
    result["cl_report"] = df_cl_report
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
    tmp_dir = tempfile.gettempdir()
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir, exist_ok=True)
    # Gọi các hàm export báo cáo
    export_funcs = [
        export_al_cl_report_department,
        export_sumary_attendance_report,
        export_sumary_attendance_report_department,
        export_late_in_5_miniutes_report_ho,
        export_feed_report,
        export_kpi_weekly_report_ho,
        export_kpi_weekly_report,
        export_al_cl_report_ho,
        export_al_cl_report,
        export_al_cl_report_severance,
    ]
    public_host = os.getenv("MINIO_PUBLIC_HOST", "localhost")
    links = {}
    for func in export_funcs:
        try:
            file_path = func(data, tmp_dir)
            if file_path and os.path.exists(file_path):
                object_name = os.path.basename(file_path)
                client.fput_object(MINIO_BUCKET, object_name, file_path)
                links[object_name] = f"http://{public_host}:9000/{MINIO_BUCKET}/{object_name}?response-content-disposition=attachment"
        except Exception as ex:
            print(f"[ETL] Export or upload failed for {func.__name__}: {ex}")
    return links

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
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    etl_job()
