import xmlrpc.client

REALATTENDANT_HOST = "https://admin.hinosoft.com"
DB_NAME = "odoo"
USERNAME = "admin"
PASSWORD = "admin"

# Đăng nhập Odoo, trả về uid và common/proxy object
def odoo_login(username=USERNAME, password=PASSWORD):
    common = xmlrpc.client.ServerProxy(f"{REALATTENDANT_HOST}/xmlrpc/2/common")
    uid = common.authenticate(DB_NAME, username, password, {})
    if not uid:
        raise Exception("Đăng nhập Odoo thất bại!")
    models = xmlrpc.client.ServerProxy(f"{REALATTENDANT_HOST}/xmlrpc/2/object")
    return uid, common, models

# Lấy danh sách giáo viên từ op.faculty (liên kết emp_id sang hr.employee)
def get_faculty_list(fields=None):
    if fields is None:
        fields = [
            'id', 'name', 'emp_id', 'active', 'email', 'phone', 'company_id', 'birth_date', 'avatar_128', 'active_lang_count'
        ]
    uid, _, models = odoo_login()
    faculty_ids = models.execute_kw(DB_NAME, uid, PASSWORD, 'op.faculty', 'search', [[['active', '=', True]]])
    faculties = models.execute_kw(DB_NAME, uid, PASSWORD, 'op.faculty', 'read', [faculty_ids, fields])
    return faculties

# Lấy thông tin nhân viên từ emp_id (nếu cần)
def get_employee_by_id(emp_id, fields=None):
    if fields is None:
        fields = ['id', 'name', 'work_email', 'work_phone', 'job_title', 'department_id']
    uid, _, models = odoo_login()
    employees = models.execute_kw(DB_NAME, uid, PASSWORD, 'hr.employee', 'read', [[emp_id], fields])
    return employees[0] if employees else None

def get_employee_by_user_id(user_id, fields=None):
    """
    Lấy thông tin nhân viên (employee) theo user_id (uid).
    Trả về phần tử đầu tiên nếu có nhiều kết quả, None nếu không có.
    """
    if fields is None:
        fields = ['id', 'name', 'work_email', 'work_phone', 'job_title', 'department_id', 'user_id']
    uid, _, models = odoo_login()
    emp_ids = models.execute_kw(DB_NAME, uid, PASSWORD, 'hr.employee', 'search', [[['user_id', '=', user_id]]])
    if not emp_ids:
        return None
    employees = models.execute_kw(DB_NAME, uid, PASSWORD, 'hr.employee', 'read', [emp_ids, fields])
    return employees[0] if employees else None

def get_employees_by_user_id(user_id, fields=None):
    """
    Lấy danh sách nhân viên (employee) theo user_id (uid).
    Trả về list các employee, [] nếu không có.
    """
    if fields is None:
        fields = ['id', 'name', 'work_email', 'work_phone', 'job_title', 'department_id', 'user_id']
    uid, _, models = odoo_login()
    emp_ids = models.execute_kw(DB_NAME, uid, PASSWORD, 'hr.employee', 'search', [[['user_id', '=', user_id]]])
    if not emp_ids:
        return []
    employees = models.execute_kw(DB_NAME, uid, PASSWORD, 'hr.employee', 'read', [emp_ids, fields])
    return employees

# Lấy danh sách các lớp (op.session) mà giáo viên dạy theo faculty_id (giáo viên), có thể lọc theo active, thời gian, ...
def get_sessions_by_faculty(faculty_id, fields=None, active=True, start_date=None, end_date=None):
    if fields is None:
        fields = [
            'id', 'name', 'course_id', 'subject_id', 'start_datetime', 'end_datetime', 'faculty_id', 'classroom_id', 'batch_id', 'active', 'state'
        ]
    uid, _, models = odoo_login()
    domain = [['faculty_id', '=', faculty_id]]
    if active is not None:
        domain.append(['active', '=', active])
    if start_date:
        domain.append(['start_datetime', '>=', start_date])
    if end_date:
        domain.append(['end_datetime', '<=', end_date])
    session_ids = models.execute_kw(DB_NAME, uid, PASSWORD, 'op.session', 'search', [domain])
    sessions = models.execute_kw(DB_NAME, uid, PASSWORD, 'op.session', 'read', [session_ids, fields])
    return sessions

# Lấy thông tin account (user) gồm: faculty info, student info theo user_id và company_id
def get_account_info(user_id, company_id=2):
    uid, _, models = odoo_login()
    # Tìm faculty info qua employee -> faculty
    emp_domain = [['user_id', '=', user_id], ['company_id', '=', company_id]]
    emp_ids = models.execute_kw(DB_NAME, uid, PASSWORD, 'hr.employee', 'search', [emp_domain])
    faculty = None
    if emp_ids:
        faculty_domain = [['emp_id', '=', emp_ids[0]]]
        faculty_ids = models.execute_kw(DB_NAME, uid, PASSWORD, 'op.faculty', 'search', [faculty_domain])
        if faculty_ids:
            faculty = models.execute_kw(DB_NAME, uid, PASSWORD, 'op.faculty', 'read', [faculty_ids, ['id', 'name', 'emp_id', 'active']])[0]
    # Tìm student info
    student_domain = [['user_id', '=', user_id], ['company_id', '=', company_id]]
    student_ids = models.execute_kw(DB_NAME, uid, PASSWORD, 'op.student', 'search', [student_domain])
    student = None
    if student_ids:
        student = models.execute_kw(DB_NAME, uid, PASSWORD, 'op.student', 'read', [student_ids, ['id', 'name', 'user_id', 'company_id', 'active']])[0]
    return {
        'faculty': faculty,
        'student': student
    }

def get_all_employees(fields=None):
    """
    Lấy danh sách tất cả nhân viên (employee) trong hệ thống.
    Trả về list các employee, [] nếu không có.
    """
    if fields is None:
        fields = ['id', 'name', 'work_email', 'work_phone', 'job_title', 'department_id', 'user_id']
    uid, _, models = odoo_login()
    emp_ids = models.execute_kw(DB_NAME, uid, PASSWORD, 'hr.employee', 'search', [[]])
    if not emp_ids:
        return []
    employees = models.execute_kw(DB_NAME, uid, PASSWORD, 'hr.employee', 'read', [emp_ids, fields])
    return employees

def get_all_equipments(fields=None):
    """
    Lấy danh sách tất cả thiết bị (maintenance.equipment) trong hệ thống.
    Trả về list các thiết bị, [] nếu không có.
    """
    if fields is None:
        fields = [
            'id', 'name', 'active', 'serial_no', 'category_id', 'company_id', 'department_id', 'employee_id',
            'owner_user_id', 'partner_id', 'partner_ref', 'technician_user_id', 'warranty_date', 'scrap_date',
            'note', 'cost', 'assign_date', 'effective_date', 'expected_mtbf', 'mtbf', 'mttr',
            'estimated_next_failure', 'color', 'display_name', 'equipment_assign_to', 'equipment_properties',
            'activity_state', 'activity_type_id', 'activity_user_id', 'activity_date_deadline',
            'activity_summary', 'activity_type_icon', 'activity_exception_icon', 'activity_exception_decoration',
            'activity_ids', 'activity_calendar_event_id', 'create_date', 'create_uid', 'write_date',
            'message_ids', 'message_is_follower', 'message_needaction', 'message_needaction_counter',
            'message_partner_ids', 'model', 'my_activity_date_deadline', 'rating_ids', 'website_message_ids',
            'has_message'
        ]
    uid, _, models = odoo_login()
    equipment_ids = models.execute_kw(DB_NAME, uid, PASSWORD, 'maintenance.equipment', 'search', [[]])
    if not equipment_ids:
        return []
    equipments = models.execute_kw(DB_NAME, uid, PASSWORD, 'maintenance.equipment', 'read', [equipment_ids, fields])
    return equipments
