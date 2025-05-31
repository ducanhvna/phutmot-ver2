import os
import xmlrpc.client
import pandas as pd
import calendar
from datetime import datetime, timedelta

ODOO_BASE_URL = "https://hrm.mandalahotel.com.vn"
ODOO_DB = "apechrm_product_v3"
ODOO_USERNAME = "admin_ho"
ODOO_PASSWORD = "43a824d3a724da2b59d059d909f13ba0c38fcb82"
# Extract helpers for Odoo models

def extract_employees(models, uid, limit, offset=0, startdate=None, enddate=None, fields=None):
    default_fields = ['id', 'name', 'user_id', 'employee_ho', 'part_time_company_id', 'part_time_department_id',
                'company_id', 'code', 'department_id', 'time_keeping_code', 'job_title',
                'probationary_contract_termination_date', 'severance_day', 'workingday',
                'probationary_salary_rate', 'resource_calendar_id', 'date_sign', 'level', 'active']
    fields = fields or default_fields
    if startdate and enddate:
        domain = ["|", ("active", ">=", False), ("active", "=", True)]
    else:
        domain = []
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.employee', 'search_read', [domain, fields], {'limit': limit, 'offset': offset})

def extract_contracts(models, uid, limit, offset=0, startdate=None, enddate=None, fields=None):
    default_fields = [
        'id', 'name', 'employee_id', 'date_start', 'date_end', 'wage', 'state',
        'minutes_per_day', 'employee_code', 'resource_calendar_id', 'active', 'company_id', 'contract_type_id'
    ] 
    fields = fields or default_fields

    # Lấy thời gian hiện tại làm dt
    dt = datetime.now()
    year = dt.year + (dt.month // 12)
    month = dt.month % 12 + 1
    last_day = calendar.monthrange(year, month)[1]
    enddate = datetime(year, month, last_day).strftime("%Y-%m-%d")
    # Bổ sung domain: (date_start <= enddate) & ((active=True)|(active=False))
    domain = ["&", ("date_start", "<=", enddate), "|", ("active", "=", True), ("active", "=", False)]

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

def extract_apec_attendance_report(models, uid, limit, offset=0, startdate=None, enddate=None, fields=None):
    default_fields = [
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
    fields = fields or default_fields
    if startdate and enddate:
        domain = ["&", ("date", ">=", startdate), ("date", "<=", enddate)]
    else:
        domain = []
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.apec.attendance.report', 'search_read', [domain, fields], {'limit': limit, 'offset': offset})

def extract_upload_attendance(models, uid, limit, offset=0, startdate=None, enddate=None, fields=None):
    default_fields = ['id', 'year', 'month', 'template', 'company_id', 'department_id', 'url'
    ]
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

def extract_attendance_trans(models, uid, limit, offset=0, startdate=None, enddate=None, fields=None):
    default_fields = ['id', 'name', 'day', 'time', 'in_out']
    fields = fields or default_fields
    if startdate and enddate:
        domain = ["&", ("day", ">=", startdate), ("day", "<=", enddate)]
    else:
        domain = []
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.attendance.trans', 'search_read', [domain, fields], {'limit': limit, 'offset': offset})

def extract_shifts(models, uid, limit, offset=0, fields=None):
    default_fields = [
        'id', 'name', 'start_work_time', 'end_work_time', 'total_work_time',
        'start_rest_time', 'end_rest_time', 'company_id', 'rest_shifts', 'fix_rest_time',
        'night', 'night_eat', 'dinner', 'lunch', 'breakfast', 'efficiency_factor',
        'minutes_working_not_reduced'
    ]
    fields = fields or default_fields
    domain = []
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'shifts', 'search_read', [domain, fields], {'limit': limit, 'offset': offset})
