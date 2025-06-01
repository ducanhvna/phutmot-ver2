import os
import xmlrpc.client
import pandas as pd
from minio import Minio
# --- Bổ sung: Tính khoảng thời gian tháng hiện tại, tháng trước, tháng sau ---
from datetime import datetime, timedelta
import calendar
import tempfile
from .report_exporters import (
    export_al_cl_report_department,
    export_summary_attendance_report,
    export_sumary_attendance_report_department,
    export_late_in_5_miniutes_report,
    export_feed_report,
    export_kpi_weekly_report_ho,
    export_kpi_weekly_report,
    export_al_cl_report_ho,
    export_al_cl_report,
    export_json_report,
    export_al_cl_report_severance,
)
from .transform_helpers import add_name_field, process_report_raw, transform_apec_attendance_report, add_mis_id_by_company_id, add_mis_id_by_company_name
from .extract_helpers import (
    extract_employees,
    extract_contracts,
    extract_companies,
    extract_leaves,
    extract_attendance,
    extract_apec_attendance_report,
    extract_upload_attendance,
    extract_kpi_weekly_report_summary,
    extract_hr_weekly_report,
    extract_al_report,
    extract_cl_report,
    extract_attendance_trans,
    extract_shifts,
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

# 1. Extract tổng hợp với phân trang

def extract_from_odoo_and_save_to_minio(pagesize=100, startdate=None, enddate=None):

    now = datetime.now()
    # Tháng hiện tại
    first_day_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day_this_month = now.replace(day=calendar.monthrange(now.year, now.month)[1], hour=23, minute=59, second=59, microsecond=999999)
    # Tháng trước
    prev_month = (now.month - 1) if now.month > 1 else 12
    prev_year = now.year if now.month > 1 else now.year - 1
    first_day_prev_month = first_day_this_month.replace(year=prev_year, month=prev_month)
    last_day_prev_month = first_day_this_month - timedelta(seconds=1)
    # Tháng sau
    next_month = (now.month + 1) if now.month < 12 else 1
    next_year = now.year if now.month < 12 else now.year + 1
    first_day_next_month = (last_day_this_month + timedelta(seconds=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    last_day_next_month = first_day_next_month.replace(day=calendar.monthrange(next_year, next_month)[1], month=next_month, year=next_year, hour=23, minute=59, second=59, microsecond=999999)
    # Lấy str theo định dạng YYYY-MM-DD
    first_day_prev_month_str = first_day_prev_month.strftime('%Y-%m-%d')
    last_day_prev_month_str = last_day_prev_month.strftime('%Y-%m-%d')
    first_day_this_month_str = first_day_this_month.strftime('%Y-%m-%d')
    last_day_this_month_str = last_day_this_month.strftime('%Y-%m-%d')
    first_day_next_month_str = first_day_next_month.strftime('%Y-%m-%d')
    last_day_next_month_str = last_day_next_month.strftime('%Y-%m-%d')
    # In ra để debug
    print(f"[ETL] Tháng trước: {first_day_prev_month_str} - {last_day_prev_month_str}")
    print(f"[ETL] Tháng này: {first_day_this_month_str} - {last_day_this_month_str}")
    print(f"[ETL] Tháng sau: {first_day_next_month_str} - {last_day_next_month_str}")

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
        extract_apec_attendance_report: 'hr.apec.attendance.report',
        extract_upload_attendance: 'hr.upload.attendance',
        extract_kpi_weekly_report_summary: 'kpi.weekly.report.summary',
        extract_hr_weekly_report: 'hr.weekly.report',
        extract_al_report: 'hr.al.report',
        extract_cl_report: 'hr.cl.report',
        extract_attendance_trans: 'hr.attendance.trans',
        extract_shifts: 'shifts',
    }
    def fetch_all(extract_func, fields, **kwargs):
        all_data = []
        offset = 0
        errors = []
        model_name = extract_func_to_model.get(extract_func)
        if model_name:
            try:
                valid_fields = set(models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD, model_name, 'fields_get', [], {}).keys())
                filtered_fields = [f for f in fields if f in valid_fields]
                missing_fields = [f for f in fields if f not in valid_fields]
                for f in missing_fields:
                    errors.append({
                        'model': model_name,
                        'field': f,
                        'status': 'thiếu',
                        'message': f"Field '{f}' không tồn tại trên model '{model_name}'"
                    })
            except Exception as ex:
                filtered_fields = fields
                errors.append({
                    'model': model_name,
                    'field': None,
                    'status': 'lỗi',
                    'message': f"Không kiểm tra được fields cho model {model_name}: {ex}"
                })
        else:
            filtered_fields = fields
        while True:
            batch = extract_func(models, uid, 100, offset, fields=filtered_fields, **kwargs)
            if not batch:
                break
            all_data.extend(batch)
            if len(batch) < 100:
                break
            offset += 100
        print(f"[ETL] {extract_func.__name__} offset={offset} batch_size={len(all_data) if all_data else 0}")
        return all_data, errors
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
    leaves_fields = ['id', 'name', 'employee_id', 'holiday_status_id', 'date_from', 'date_to', 'state'
    ]
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
    apec_attendance_fields = [
        'id', 'employee_name', 'date', 'shift_name', 'employee_code', 'company', 'additional_company',
        'shift_start', 'shift_end', 'rest_start', 'rest_end', 'rest_shift', 'probation_completion_wage',
        'total_shift_work_time', 'total_work_time', 'time_keeping_code', 'kid_time',
        'department', 'attendance_attempt_1', 'attendance_attempt_2', 'minutes_working_reduced',
        'attendance_attempt_3', 'attendance_attempt_4', 'attendance_attempt_5',
        'attendance_attempt_6', 'attendance_attempt_7', 'attendance_attempt_8',
        'attendance_attempt_9', 'attendance_attempt_10', 'attendance_attempt_11',
        'attendance_attempt_12', 'attendance_attempt_13', 'attendance_attempt_14',
        'attendance_inout_1', 'attendance_inout_2', 'attendance_inout_3',
        'attendance_inout_4', 'attendance_inout_5', 'attendance_inout_6',
        'attendance_inout_7', 'attendance_inout_8', 'attendance_inout_9', 'amount_al_reserve', 'amount_cl_reserve',
        'attendance_inout_10', 'attendance_inout_11', 'attendance_inout_12',
        'attendance_inout_13', 'attendance_inout_14', 'attendance_inout_15', 'actual_total_work_time', 'standard_working_day',
        'attendance_attempt_15', 'last_attendance_attempt', 'attendance_inout_last', 'night_hours_normal', 'night_hours_holiday', 'probation_wage_rate',
        'split_shift', 'missing_checkin_break', 'leave_early', 'attendance_late', 'night_shift', 'minute_worked_day_holiday',
        'total_attendance', 'ot_holiday', 'ot_normal'
    ]
    attendance_trans_fields = ['id', 'name', 'day', 'time', 'in_out']
    shifts_fields = [
        'id', 'name', 'start_work_time', 'end_work_time', 'total_work_time',
        'start_rest_time', 'end_rest_time', 'company_id', 'rest_shifts', 'fix_rest_time',
        'night', 'night_eat', 'dinner', 'lunch', 'breakfast', 'efficiency_factor',
        'minutes_working_not_reduced'
    ]
    # Gọi extract với fields truyền vào
    employees, extract_errors = fetch_all(extract_employees, employees_fields, startdate=startdate, enddate=enddate)
    contracts, err = fetch_all(extract_contracts, contracts_fields, startdate=startdate, enddate=enddate)
    extract_errors.extend(err)
    companies, err = fetch_all(extract_companies, companies_fields)
    extract_errors.extend(err)
    leaves, err = fetch_all(extract_leaves, leaves_fields, startdate=startdate, enddate=enddate)
    extract_errors.extend(err)
    # attendance, err = fetch_all(extract_attendance, attendance_fields, startdate=startdate, enddate=enddate)
    # extract_errors.extend(err)
    upload_attendance, err = fetch_all(extract_upload_attendance, upload_attendance_fields)
    extract_errors.extend(err)
    kpi_weekly_report_summary, err = fetch_all(extract_kpi_weekly_report_summary, kpi_weekly_report_summary_fields, startdate=startdate, enddate=enddate)
    extract_errors.extend(err)
    hr_weekly_report, err = fetch_all(extract_hr_weekly_report, hr_weekly_report_fields, startdate=startdate, enddate=enddate)
    extract_errors.extend(err)
    al_report, err = fetch_all(extract_al_report, al_report_fields, startdate=startdate, enddate=enddate)
    extract_errors.extend(err)
    cl_report, err = fetch_all(extract_cl_report, cl_report_fields, startdate=startdate, enddate=enddate)
    extract_errors.extend(err)
    apec_attendance_prev_report, err = fetch_all(extract_apec_attendance_report, apec_attendance_fields, startdate=first_day_prev_month_str, enddate=last_day_prev_month_str)
    extract_errors.extend(err)
    apec_attendance_report, err = fetch_all(extract_apec_attendance_report, apec_attendance_fields, startdate=first_day_this_month_str, enddate=last_day_this_month_str)
    extract_errors.extend(err)
    attendance_trans, err = fetch_all(extract_attendance_trans, attendance_trans_fields, startdate=first_day_prev_month_str, enddate=last_day_next_month_str)
    extract_errors.extend(err)
    shifts, err = fetch_all(extract_shifts, shifts_fields)
    extract_errors.extend(err)
    data = {
        'first_day_this_month': first_day_this_month,
        'last_day_this_month': last_day_this_month,
        'first_day_prev_month': first_day_prev_month,
        'last_day_prev_month': last_day_prev_month,
        'first_day_next_month': first_day_next_month,
        'last_day_next_month': last_day_next_month,
        'employees': employees,
        'contracts': contracts,
        'companies': companies,
        'leaves': leaves,
        # 'attendance': attendance,  # BỎ HOÀN TOÀN attendance
        'upload_attendance': upload_attendance,
        'kpi_weekly_report_summary': kpi_weekly_report_summary,
        'hr_weekly_report': hr_weekly_report,
        'al_report': al_report,
        'cl_report': cl_report,
        'apec_attendance_report': apec_attendance_report,
        'apec_attendance_prev_report': apec_attendance_prev_report,
        'attendance_trans': attendance_trans,
        'shifts': shifts,
        'extract_errors': extract_errors,
    }
    print("Save raw data to Excel and upload to MinIO...")
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
    file_path = os.path.join(tmp_dir, f"odoo_raw_{datetime.now().strftime('%Y%m%d')}.xlsx")
    with pd.ExcelWriter(file_path) as writer:
        for key, value in data.items():
            # Bỏ qua các giá trị là datetime, date, hoặc string (chỉ ghi DataFrame hoặc list/dict phù hợp)
            if isinstance(value, (datetime, str)):
                continue
            # Nếu là list các dict hoặc list các list, convert sang DataFrame
            if isinstance(value, list) and value and isinstance(value[0], (dict, list)):
                df = pd.DataFrame(value)
            elif isinstance(value, pd.DataFrame):
                df = value
            else:
                # Bỏ qua các kiểu không phù hợp
                continue
            if not df.empty:
                df.to_excel(writer, sheet_name=key, index=False)
            else:
                pd.DataFrame().to_excel(writer, sheet_name=key, index=False)
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
def transform(data, startdate=None, enddate=None):
    # Chuẩn hóa, loại bỏ test, merge dữ liệu, tính toán tổng hợp
    result = {}
    # Employees
    list_employees = data["employees"]
    add_name_field(list_employees, id_field="company_id", name_field="company_name")
    add_name_field(list_employees, id_field="department_id", name_field="department_name")
    add_name_field(list_employees, id_field="user_id", name_field="user_name")
    add_name_field(list_employees, id_field="part_time_company_id", name_field="part_time_company_name")
    add_name_field(list_employees, id_field="part_time_department_id", name_field="part_time_department_name")
    add_name_field(list_employees, id_field="resource_calendar_id", name_field="resource_calendar_name")
    # Bổ sung mis_id
    add_mis_id_by_company_id(list_employees, data["companies"])
    df_emp = pd.DataFrame(list_employees)
    if not df_emp.empty:
        df_emp = df_emp.drop_duplicates(subset=["id"])
        df_emp = df_emp[~df_emp["name"].str.lower().str.contains("test")]
    result["employees"] = df_emp
    # Chuẩn hóa employees_dict (dict theo code)
    from .transform_helpers import employees_list_to_dict, contracts_list_to_dicts_by_month
    result["employees_dict"] = employees_list_to_dict(df_emp)
    # Contracts
    list_contracts = data["contracts"]
    add_name_field(list_contracts, id_field="employee_id", name_field="employee_name")
    add_name_field(list_contracts, id_field="company_id", name_field="company_name")
    add_name_field(list_contracts, id_field="resource_calendar_id", name_field="resource_calendar_name")
    add_mis_id_by_company_id(list_contracts, data["companies"])
    df_contracts = pd.DataFrame(list_contracts)
    if not df_contracts.empty:
        df_contracts["date_start"] = pd.to_datetime(df_contracts["date_start"], errors="coerce")
        df_contracts["date_end"] = pd.to_datetime(df_contracts["date_end"], errors="coerce")
    result["contracts"] = df_contracts
    # Chuẩn hóa contracts_dict (3 dict theo employee_code, theo tháng)
    contracts_dict, contracts_prev_dict, contracts_next_dict = contracts_list_to_dicts_by_month(df_contracts)
    result["contracts_dict"] = contracts_dict
    result["contracts_prev_dict"] = contracts_prev_dict
    result["contracts_next_dict"] = contracts_next_dict
    # Companies
    df_companies = pd.DataFrame(data["companies"])
    result["companies"] = df_companies
    # Leaves
    list_leaves = data["leaves"]
    add_name_field(list_leaves, id_field="employee_id", name_field="employee_name")
    add_name_field(list_leaves, id_field="company_id", name_field="company_name")
    add_name_field(list_leaves, id_field="department_id", name_field="department_name")
    add_mis_id_by_company_id(list_leaves, data["companies"])
    df_leaves = pd.DataFrame(list_leaves)
    if not df_leaves.empty:
        df_leaves["date_from"] = pd.to_datetime(df_leaves["date_from"], errors="coerce")
        df_leaves["date_to"] = pd.to_datetime(df_leaves["date_to"], errors="coerce")
    result["leaves"] = df_leaves
    # Chuẩn hóa leaves_dict (dict theo employee_code)
    from .transform_helpers import leaves_list_to_dict
    result["leaves_dict"] = leaves_list_to_dict(df_leaves)
    # Upload Attendance
    list_upload_attendance = data["upload_attendance"]
    add_name_field(list_upload_attendance, id_field="company_id", name_field="company_name")
    add_name_field(list_upload_attendance, id_field="department_id", name_field="department_name")
    add_mis_id_by_company_id(list_upload_attendance, data["companies"])
    df_upload_attendance = pd.DataFrame(list_upload_attendance)
    result["upload_attendance"] = df_upload_attendance
    # KPI Weekly Report Summary
    df_kpi_weekly = pd.DataFrame(data["kpi_weekly_report_summary"])
    if not df_kpi_weekly.empty and "date" in df_kpi_weekly:
        df_kpi_weekly["date"] = pd.to_datetime(df_kpi_weekly["date"], errors="coerce")
    result["kpi_weekly_report_summary"] = df_kpi_weekly
    # Chuẩn hóa kpi_weekly_report_summary_dict (dict theo employee_code)
    from .transform_helpers import kpi_weekly_report_summary_list_to_dict
    result["kpi_weekly_report_summary_dict"] = kpi_weekly_report_summary_list_to_dict(df_kpi_weekly)
    # HR Weekly Report
    list_hr_weekly = data["hr_weekly_report"]
    add_name_field(list_hr_weekly, id_field="employee_id", name_field="employee_name")
    add_name_field(list_hr_weekly, id_field="company_id", name_field="company_name")
    add_name_field(list_hr_weekly, id_field="department_id", name_field="department_name")
    add_mis_id_by_company_id(list_hr_weekly, data["companies"])
    df_hr_weekly = pd.DataFrame(list_hr_weekly)
    if not df_hr_weekly.empty and "date" in df_hr_weekly:
        df_hr_weekly["date"] = pd.to_datetime(df_hr_weekly["date"], errors="coerce")
    result["hr_weekly_report"] = df_hr_weekly
    # Chuẩn hóa hr_weekly_report_dict (dict theo employee_code)
    from .transform_helpers import hr_weekly_report_list_to_dict
    result["hr_weekly_report_dict"] = hr_weekly_report_list_to_dict(df_hr_weekly)
    # AL Report
    list_al_report = data["al_report"]
    add_name_field(list_al_report, id_field="employee_id", name_field="employee_name")
    add_name_field(list_al_report, id_field="company_id", name_field="company_name")
    add_name_field(list_al_report, id_field="department_id", name_field="department_name")
    add_name_field(list_al_report, id_field="part_time_company_id", name_field="part_time_company_name")
    add_mis_id_by_company_id(list_al_report, data["companies"])
    df_al_report = pd.DataFrame(list_al_report)
    if not df_al_report.empty:
        df_al_report["date_calculate_leave"] = pd.to_datetime(df_al_report["date_calculate_leave"])
    result["al_report"] = df_al_report
    # Chuẩn hóa al_report_dict (dict theo employee_code, giảm dần theo date_calculate_leave)
    from .transform_helpers import al_report_list_to_dict
    result["al_report_dict"] = al_report_list_to_dict(df_al_report)
    # CL Report
    list_cl_report = data["cl_report"]
    add_name_field(list_cl_report, id_field="employee_id", name_field="employee_name")
    add_name_field(list_cl_report, id_field="company_id", name_field="company_name")
    add_name_field(list_cl_report, id_field="department_id", name_field="department_name")
    add_mis_id_by_company_id(list_cl_report, data["companies"])
    df_cl_report = pd.DataFrame(list_cl_report)
    if not df_cl_report.empty:
        df_cl_report["date_calculate"] = pd.to_datetime(df_cl_report["date_calculate"])
    result["cl_report"] = df_cl_report
    # Chuẩn hóa cl_report_dict (dict theo employee_code, giảm dần theo date_calculate)
    from .transform_helpers import cl_report_list_to_dict
    result["cl_report_dict"] = cl_report_list_to_dict(df_cl_report)
    # APEC Attendance Report (thay thế attendance)
    # Bổ sung mis_id cho DataFrame
    add_mis_id_by_company_name(data["apec_attendance_prev_report"], data["companies"])
    df_apec_attendance_prev = pd.DataFrame(data["apec_attendance_prev_report"])
    # Sử dụng transform_apec_attendance_report để sinh couple, couple_out_in, tổng out_ho, các trường datetime
    if not df_apec_attendance_prev.empty:
        df_apec_attendance_prev = transform_apec_attendance_report(df_apec_attendance_prev)
    result["apec_attendance_report_prev"] = df_apec_attendance_prev
    # Chuẩn hóa apec_attendance_report_dict (dict theo employee_code, tăng dần theo date)
    from .transform_helpers import apec_attendance_report_list_to_dict
    result["apec_attendance_report_prev_dict"] = apec_attendance_report_list_to_dict(df_apec_attendance_prev)

    # Bổ sung mis_id cho DataFrame
    add_mis_id_by_company_name(data["apec_attendance_report"], data["companies"])
    df_apec_attendance = pd.DataFrame(data["apec_attendance_report"])
    # Sử dụng transform_apec_attendance_report để sinh couple, couple_out_in, tổng out_ho, các trường datetime
    if not df_apec_attendance.empty:
        df_apec_attendance = transform_apec_attendance_report(df_apec_attendance)
    result["apec_attendance_report"] = df_apec_attendance
    # Chuẩn hóa apec_attendance_report_dict (dict theo employee_code, tăng dần theo date)
    result["apec_attendance_report_dict"] = apec_attendance_report_list_to_dict(df_apec_attendance)
    # Shifts: bổ sung trường company_name và mis_id
    list_shifts = data.get("shifts", [])
    add_name_field(list_shifts, id_field="company_id", name_field="company_name")
    add_mis_id_by_company_id(list_shifts, data["companies"])
    result["shifts"] = pd.DataFrame(list_shifts)
    # Chuẩn hóa shifts_dict (dict theo mis_id)
    from .transform_helpers import shifts_list_to_dict
    result["shifts_dict"] = shifts_list_to_dict(result["shifts"])
    # Bổ sung cho các dữ liệu khác có *_id nếu cần
    # Có thể bổ sung merge, join, tính toán tổng hợp ở đây nếu cần
    # Chuẩn hóa attendance_trans_dict (dict theo name, giảm dần theo time)
    from .transform_helpers import attendance_trans_list_to_dict
    result["attendance_trans_dict"] = attendance_trans_list_to_dict(pd.DataFrame(data["attendance_trans"]))
    return result

# 3. Load to MinIO (public-read, truy cập qua port 9000 sẽ tải về trực tiếp)
def load_to_minio(data, report_date=None):
    """
    Lưu từng loại báo cáo cho từng công ty lên MinIO, đặt tên chuẩn.
    report_date: string yyyy-mm-dd hoặc None (mặc định lấy ngày hiện tại)
    """
    first_day_this_month = data.get("first_day_this_month")
    last_day_this_month = data.get("last_day_this_month")
    first_day_prev_month = data.get("first_day_prev_month")
    last_day_prev_month = data.get("last_day_prev_month")
    first_day_next_month = data.get("first_day_next_month")
    last_day_next_month = data.get("last_day_next_month")
    if not report_date:
        report_date = datetime.now().strftime("%Y%m%d")
    report_time = datetime.now().strftime("%H%M%S")
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
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir, exist_ok=True)
    # public_host = os.getenv("MINIO_PUBLIC_HOST", "localhost")
    links = {}
    # Lưu employees_dict (nếu có) ra file json chuẩn bằng export_json_report
    employees_dict = data.get("employees_dict")
    if employees_dict:
        file_name = f"1__employees_dict__{report_date}.json"
        file_name_on_disk = f"1__employees_dict__{report_date}__{report_time}.json"
        file_path = export_json_report(employees_dict, tmp_dir, file_name_on_disk)
        client.fput_object(MINIO_BUCKET, file_name, file_path)
        url = client.presigned_get_object(MINIO_BUCKET, file_name)
        links[file_name] = url
        # Bulk upsert vào DB sau khi lưu file json employees_dict
        try:
            from app.db import SessionLocal
            from app.models.hrms.employee import bulk_upsert_employees_dict_to_db
            db = SessionLocal()
            bulk_upsert_employees_dict_to_db(employees_dict, db, created_by="etl")
            db.close()
        except Exception as ex:
            print(f"[ETL] Bulk upsert employees_dict to DB failed: {ex}")
    # Lưu contracts_dict (nếu có) ra file json chuẩn hóa
    contracts_dict = data.get("contracts_dict")
    contracts_prev_dict = data.get("contracts_prev_dict")
    contracts_next_dict = data.get("contracts_next_dict")
    if contracts_dict:
        file_name = f"1__contracts_dict__{report_date}.json"
        file_name_on_disk = f"1__contracts_dict__{report_date}__{report_time}.json"
        file_path = export_json_report(contracts_dict, tmp_dir, file_name_on_disk)
        client.fput_object(MINIO_BUCKET, file_name, file_path)
        url = client.presigned_get_object(MINIO_BUCKET, file_name)
        links[file_name] = url
    if contracts_prev_dict:
        file_name_prev = f"1__contracts_prev_dict__{report_date}.json"
        file_name_on_disk_prev = f"1__contracts_prev_dict__{report_date}__{report_time}.json"
        file_path_prev = export_json_report(contracts_prev_dict, tmp_dir, file_name_on_disk_prev)
        client.fput_object(MINIO_BUCKET, file_name_prev, file_path_prev)
        url_prev = client.presigned_get_object(MINIO_BUCKET, file_name_prev)
        links[file_name_prev] = url_prev
    if contracts_next_dict:
        file_name_next = f"1__contracts_next_dict__{report_date}.json"
        file_name_on_disk_next = f"1__contracts_next_dict__{report_date}__{report_time}.json"
        file_path_next = export_json_report(contracts_next_dict, tmp_dir, file_name_on_disk_next)
        client.fput_object(MINIO_BUCKET, file_name_next, file_path_next)
        url_next = client.presigned_get_object(MINIO_BUCKET, file_name_next)
        links[file_name_next] = url_next
    # Lưu leaves_dict (nếu có) ra file json chuẩn hóa
    leaves_dict = data.get("leaves_dict")
    if leaves_dict:
        file_name = f"1__leaves_dict__{report_date}.json"
        file_name_on_disk = f"1__leaves_dict__{report_date}__{report_time}.json"
        file_path = export_json_report(leaves_dict, tmp_dir, file_name_on_disk)
        client.fput_object(MINIO_BUCKET, file_name, file_path)
        url = client.presigned_get_object(MINIO_BUCKET, file_name)
        links[file_name] = url
    # Lưu kpi_weekly_report_summary_dict (nếu có) ra file json chuẩn hóa
    kpi_weekly_report_summary_dict = data.get("kpi_weekly_report_summary_dict")
    if kpi_weekly_report_summary_dict:
        file_name = f"1__kpi_weekly_report_summary_dict__{report_date}.json"
        file_name_on_disk = f"1__kpi_weekly_report_summary_dict__{report_date}__{report_time}.json"
        file_path = export_json_report(kpi_weekly_report_summary_dict, tmp_dir, file_name_on_disk)
        client.fput_object(MINIO_BUCKET, file_name, file_path)
        url = client.presigned_get_object(MINIO_BUCKET, file_name)
        links[file_name] = url
    # Lưu hr_weekly_report_dict (nếu có) ra file json chuẩn hóa
    hr_weekly_report_dict = data.get("hr_weekly_report_dict")
    if hr_weekly_report_dict:
        file_name = f"1__hr_weekly_report_dict__{report_date}.json"
        file_name_on_disk = f"1__hr_weekly_report_dict__{report_date}__{report_time}.json"
        file_path = export_json_report(hr_weekly_report_dict, tmp_dir, file_name_on_disk)
        client.fput_object(MINIO_BUCKET, file_name, file_path)
        url = client.presigned_get_object(MINIO_BUCKET, file_name)
        links[file_name] = url
    # Lưu al_report_dict (nếu có) ra file json chuẩn hóa
    al_report_dict = data.get("al_report_dict")
    if al_report_dict:
        file_name = f"1__al_report_dict__{report_date}.json"
        file_name_on_disk = f"1_al_report_dict__{report_date}__{report_time}.json"
        file_path = export_json_report(al_report_dict, tmp_dir, file_name_on_disk)
        client.fput_object(MINIO_BUCKET, file_name, file_path)
        url = client.presigned_get_object(MINIO_BUCKET, file_name)
        links[file_name] = url
    # Lưu cl_report_dict (nếu có) ra file json chuẩn hóa
    cl_report_dict = data.get("cl_report_dict")
    if cl_report_dict:
        file_name = f"1__cl_report_dict__{report_date}.json"
        file_name_on_disk = f"1__cl_report_dict__{report_date}__{report_time}.json"
        file_path = export_json_report(cl_report_dict, tmp_dir, file_name_on_disk)
        client.fput_object(MINIO_BUCKET, file_name, file_path)
        url = client.presigned_get_object(MINIO_BUCKET, file_name)
        links[file_name] = url
    # Lưu attendance_trans_dict (nếu có) ra file json chuẩn hóa
    attendance_trans_dict = data.get("attendance_trans_dict")
    if attendance_trans_dict:
        file_name = f"1__attendance_trans_dict__{report_date}.json"
        file_name_on_disk = f"1__attendance_trans_dict__{report_date}__{report_time}.json"
        file_path = export_json_report(attendance_trans_dict, tmp_dir, file_name_on_disk)
        client.fput_object(MINIO_BUCKET, file_name, file_path)
        url = client.presigned_get_object(MINIO_BUCKET, file_name)
        links[file_name] = url
    # Lưu shifts_dict (nếu có) ra file json chuẩn hóa
    shifts_dict = data.get("shifts_dict")
    if shifts_dict:
        file_name = f"1__shifts_dict__{report_date}.json"
        file_name_on_disk = f"1__shifts_dict__{report_date}__{report_time}.json"
        file_path = export_json_report(shifts_dict, tmp_dir, file_name_on_disk)
        client.fput_object(MINIO_BUCKET, file_name, file_path)
        url = client.presigned_get_object(MINIO_BUCKET, file_name)
        links[file_name] = url
    # Lưu apec_attendance_report_dict (nếu có) ra file json chuẩn hóa
    apec_attendance_report_dict = data.get("apec_attendance_report_dict")
    if apec_attendance_report_dict:
        # Bulk upsert vào DB sau khi lưu file json apec_attendance_report_dict
        from app.db import SessionLocal
        from app.models.hrms.summary_report_monthly import bulk_upsert_summary_report_dict_to_db
        db = SessionLocal()
        year = first_day_this_month.year if first_day_this_month else datetime.now().year
        month = first_day_this_month.month if first_day_this_month else datetime.now().month
        # Parse month, year từ report_date
        # if isinstance(report_date, str) and len(report_date) >= 6:
        #     year = int(report_date[:4])
        #     month = int(report_date[4:6])
        print(f"Upserting month {month} year {year} summary reports to DB...")
        bulk_upsert_summary_report_dict_to_db(apec_attendance_report_dict, db, created_by="etl", month=month, year=year)
        db.close()
        file_name = f"1__apec_attendance_report_dict__{report_date}.json"
        file_name_on_disk = f"1__apec_attendance_report_dict__{report_date}__{report_time}.json"
        file_path = export_json_report(apec_attendance_report_dict, tmp_dir, file_name_on_disk)
        client.fput_object(MINIO_BUCKET, file_name, file_path)
        url = client.presigned_get_object(MINIO_BUCKET, file_name)
        links[file_name] = url
    
    # Lưu apec_attendance_report_dict (nếu có) ra file json chuẩn hóa
    apec_attendance_report_prev_dict = data.get("apec_attendance_report_prev_dict")
    if apec_attendance_report_prev_dict:
        # Bulk upsert vào DB sau khi lưu file json apec_attendance_report_dict
        from app.db import SessionLocal
        from app.models.hrms.summary_report_monthly import bulk_upsert_summary_report_dict_to_db
        db = SessionLocal()
        year = first_day_prev_month.year
        month = first_day_prev_month.month
        # Parse month, year từ report_date
        # if isinstance(report_date, str) and len(report_date) >= 6:
        #     year = int(report_date[:4])
        #     month = int(report_date[4:6])
        print(f"Upserting month {month} year {year} summary reports to DB...")
        bulk_upsert_summary_report_dict_to_db(apec_attendance_report_prev_dict, db, created_by="etl", month=month, year=year)
        db.close()
        file_name = f"1__apec_attendance_report_prev_dict__{report_date}.json"
        file_name_on_disk = f"1__apec_attendance_report_prev_dict__{report_date}__{report_time}.json"
        file_path = export_json_report(apec_attendance_report_prev_dict, tmp_dir, file_name_on_disk)
        client.fput_object(MINIO_BUCKET, file_name, file_path)
        url = client.presigned_get_object(MINIO_BUCKET, file_name)
        links[file_name] = url


    df_apec_attendance = data.get("apec_attendance_report")
    if isinstance(df_apec_attendance, pd.DataFrame) and not df_apec_attendance.empty:
        from .report_exporters import export_summary_attendance_report
        file_paths = export_summary_attendance_report(
            {"apec_attendance_report": df_apec_attendance},
            tmp_dir,
            data_key="apec_attendance_report"
        )
        for file_path in file_paths:
            file_name = os.path.basename(file_path).replace(" ", "_")
            client.fput_object(MINIO_BUCKET, file_name, file_path)
            url = client.presigned_get_object(MINIO_BUCKET, file_name)
            links[file_name] = url
    # Danh sách các loại báo cáo và hàm export tương ứng
    report_types = [
        # ("apec_attendance_report", export_summary_attendance_report, "apec_attendance_report"),
        ("al_report", export_al_cl_report, "al_cl_report"),
        ("feed_report", export_feed_report, "feed_report"),
        ("kpi_weekly_report_summary", export_kpi_weekly_report_ho, "kpi_weekly_report_ho"),
        ("late_in_5_miniutes", export_late_in_5_miniutes_report, "late_in_5_miniutes_report_ho"),
        # ... bổ sung các loại báo cáo khác nếu cần ...
    ]
    
    for data_key, export_func, report_type in report_types:
        df = data.get(data_key)
        if not isinstance(df, pd.DataFrame) or df.empty:
            continue
        # Group theo công ty
        company_col = 'mis_id'
        # for col in ["company", "company_name"]:
        #     if col in df.columns:
        #         company_col = col
        #         break
        # if not company_col:
        #     continue
        
        # file_path = os.path.join(tmp_dir, f"odoo_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        # with pd.ExcelWriter(file_path) as writer:
        #     for key, value in data.items():
        #         df = pd.DataFrame(value)
        #         df.to_excel(writer, sheet_name=key, index=False)
        # object_name = os.path.basename(file_path)
        # # Đảm bảo file thực sự được upload lên MinIO
        # client.fput_object(MINIO_BUCKET, object_name, file_path)
        # # Kiểm tra lại object vừa upload
        # found = False
        # for obj in client.list_objects(MINIO_BUCKET, prefix=object_name):
        #     if obj.object_name == object_name:
        #         found = True
        #         break
        # if not found:
        #     raise RuntimeError(f"File {object_name} was not uploaded to MinIO bucket {MINIO_BUCKET}")
        # url = client.presigned_get_object(MINIO_BUCKET, object_name)

        for company, group in df.groupby(company_col):
            if not isinstance(group, pd.DataFrame) or group.empty:
                continue
            safe_company = str(company).replace("/", "_").replace("\\", "_").replace(" ", "_")
            file_name = f"{safe_company}__{report_type}__{report_date}.xlsx"
            file_name_on_disk = f"{safe_company}__{report_type}__{report_date}__{report_time}.xlsx"
            file_path = os.path.join(tmp_dir, file_name_on_disk)
            # Gọi hàm export, truyền đúng data_key nếu cần
            export_func({data_key: group}, tmp_dir, data_key=data_key) if 'data_key' in export_func.__code__.co_varnames else export_func({data_key: group}, tmp_dir)
            # Nếu file đã đúng tên thì không cần rename
            if not os.path.exists(file_path):
                # Tìm file vừa tạo trong tmp_dir (có thể tên khác do hàm export mock)
                for f in os.listdir(tmp_dir):
                    if f.endswith('.xlsx') and report_type in f and (safe_company in f or len(df[company_col].unique())==1):
                        os.rename(os.path.join(tmp_dir, f), file_path)
                        break
            if os.path.exists(file_path):
                client.fput_object(MINIO_BUCKET, file_name, file_path)
                for obj in client.list_objects(MINIO_BUCKET, prefix=file_name):
                    if obj.object_name == file_name:
                        found = True
                        break
                if not found:
                    raise RuntimeError(f"File {file_name} was not uploaded to MinIO bucket {MINIO_BUCKET}")
                url = client.presigned_get_object(MINIO_BUCKET, file_name)
                # links[file_name] = f"http://{public_host}:9000/{MINIO_BUCKET}/{file_name}?response-content-disposition=attachment"
                links[file_name] = url
    # Lưu metadata file vào bảng FileMetadata
    from app.models.file_metadata import save_file_metadata_list
    save_file_metadata_list(links)
    return links

# 4. ETL Job
def etl_job(startdate=None, enddate=None):
    try:
        raw_data, raw_url = extract_from_odoo_and_save_to_minio(startdate=startdate, enddate=enddate)
        print(f"[ETL] Extract Success.")
        clean_data = transform(raw_data, startdate=startdate, enddate=enddate)
        print(f"[ETL] Transform Success.")
        report_url = load_to_minio(clean_data, f"hrms_etl_report_{datetime.now().strftime('%Y%m%d')}")
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
