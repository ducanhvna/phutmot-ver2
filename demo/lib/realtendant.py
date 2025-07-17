import json
import xmlrpc.client
import qrcode
import os
from datetime import datetime, timedelta, timedelta

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

# Lấy chi tiết công đoạn từ bảng mrp.workorder
def get_workorder_detail(workorder_id, fields=None):
    if fields is None:
        fields = [
            'id', 'name', 'workcenter_id', 'product_id', 'qty_produced', 'duration_expected', 'state'
        ]
    uid, _, models = odoo_login()
    workorders = models.execute_kw(DB_NAME, uid, PASSWORD, 'mrp.workorder', 'read', [[workorder_id], fields])
    if not workorders:
        return None
    return workorders[0]

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
def get_employee_by_id(emp_id, fields=None, user_fields=None):
    if fields is None:
        fields = ['id', 'name', 'work_email', 'work_phone', 'job_title', 'department_id', 'user_id']
    if user_fields is None:
        user_fields = ['id', 'name', 'login', 'email', 'company_id', 'active']
    uid, _, models = odoo_login()
    employees = models.execute_kw(DB_NAME, uid, PASSWORD, 'hr.employee', 'read', [[emp_id], fields])
    if not employees:
        return None
    employee = employees[0]
    user_id = employee.get('user_id')
    if user_id:
        # user_id có thể là [id, name] hoặc id, nên lấy id
        if isinstance(user_id, list):
            user_id_val = user_id[0]
        else:
            user_id_val = user_id
        users = models.execute_kw(DB_NAME, uid, PASSWORD, 'res.users', 'read', [[user_id_val], user_fields])
        employee['user_detail'] = users[0] if users else None
    else:
        employee['user_detail'] = None
    return employee

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

def get_all_mrp_productions(fields=None):
    """
    Lấy danh sách tất cả lệnh sản xuất (mrp.production) trong hệ thống.
    Trả về list các production, [] nếu không có.
    """
    if fields is None:
        fields = [
            'id', 'name', 'state', 'product_id', 'product_qty', 'product_uom_id', 'date_start', 'date_finished',
            'company_id', 'user_id', 'origin', 'bom_id', 'qty_produced', 'qty_producing', 'date_deadline',
            'create_date', 'write_date', 'create_uid', 'write_uid', 'warehouse_id', 'workcenter_id',
            'production_location_id', 'location_src_id', 'location_dest_id', 'priority', 'sale_line_id',
            'picking_type_id', 'picking_ids', 'move_raw_ids', 'move_finished_ids', 'move_byproduct_ids',
            'components_availability', 'components_availability_state', 'consumption', 'is_locked', 'is_delayed',
            'is_outdated_bom', 'is_planned', 'production_capacity', 'duration', 'duration_expected', 'extra_cost',
            'delay_alert_date', 'delivery_count', 'display_name', 'forecasted_issue', 'has_analytic_account',
            'has_message', 'json_popover', 'location_final_id', 'lot_producing_id', 'message_attachment_count',
            'message_follower_ids', 'message_has_error', 'message_has_error_counter', 'message_has_sms_error',
            'message_ids', 'message_is_follower', 'message_needaction', 'message_needaction_counter',
            'message_partner_ids', 'mrp_production_backorder_count', 'mrp_production_child_count',
            'mrp_production_source_count', 'my_activity_date_deadline', 'never_product_template_attribute_value_ids',
            'orderpoint_id', 'priority', 'procurement_group_id', 'product_description_variants', 'product_tmpl_id',
            'product_tracking', 'product_uom_category_id', 'product_uom_qty', 'product_variant_attributes',
            'propagate_cancel', 'purchase_order_count', 'rating_ids', 'reservation_state', 'reserve_visible',
            'sale_order_count', 'scrap_count', 'scrap_ids', 'search_date_category', 'show_allocation',
            'show_final_lots', 'show_lock', 'show_lot_ids', 'show_produce', 'show_produce_all', 'show_valuation',
            'unbuild_count', 'unbuild_ids', 'unreserve_visible', 'use_create_components_lots', 'valid_product_template_attribute_line_ids',
            'website_message_ids', 'activity_ids', 'activity_state', 'activity_type_id', 'activity_user_id',
            'activity_date_deadline', 'activity_summary', 'activity_type_icon', 'activity_exception_icon',
            'activity_exception_decoration', 'activity_calendar_event_id', 'all_move_ids', 'all_move_raw_ids',
            'allow_workorder_dependencies', 'backorder_sequence', 'components_availability', 'consumption',
            'finished_move_line_ids', 'move_dest_ids', 'move_raw_ids', 'move_finished_ids', 'move_byproduct_ids',
            'origin', 'priority', 'product_id', 'product_qty', 'product_uom_id', 'qty_produced', 'qty_producing',
            'state', 'user_id', 'warehouse_id', 'workorder_ids'
        ]
    uid, _, models = odoo_login()
    production_ids = models.execute_kw(DB_NAME, uid, PASSWORD, 'mrp.production', 'search', [[]])
    if not production_ids:
        return []
    productions = models.execute_kw(DB_NAME, uid, PASSWORD, 'mrp.production', 'read', [production_ids, fields])
    return productions

def get_mrp_production_detail(production_id, fields=None, workorder_fields=None, user_fields=None):
    """
    Lấy chi tiết lệnh sản xuất (mrp.production) theo id, kèm danh sách công đoạn (mrp.workorder) và chi tiết user đang tham gia công đoạn.
    """
    if fields is None:
        fields = [
            'id', 'name', 'state', 'product_id', 'product_qty', 'product_uom_id', 'date_start', 'date_finished',
            'company_id', 'user_id', 'origin', 'bom_id', 'qty_produced', 'qty_producing', 'date_deadline',
            'create_date', 'write_date', 'create_uid', 'write_uid', 'warehouse_id', 'workcenter_id',
            'production_location_id', 'location_src_id', 'location_dest_id', 'priority', 'sale_line_id',
            'picking_type_id', 'picking_ids', 'move_raw_ids', 'move_finished_ids', 'move_byproduct_ids',
            'components_availability', 'components_availability_state', 'consumption', 'is_locked', 'is_delayed',
            'is_outdated_bom', 'is_planned', 'production_capacity', 'duration', 'duration_expected', 'extra_cost',
            'delay_alert_date', 'delivery_count', 'display_name', 'forecasted_issue', 'has_analytic_account',
            'has_message', 'json_popover', 'location_final_id', 'lot_producing_id', 'message_attachment_count',
            'message_follower_ids', 'message_has_error', 'message_has_error_counter', 'message_has_sms_error',
            'message_ids', 'message_is_follower', 'message_needaction', 'message_needaction_counter',
            'message_partner_ids', 'mrp_production_backorder_count', 'mrp_production_child_count',
            'mrp_production_source_count', 'my_activity_date_deadline', 'never_product_template_attribute_value_ids',
            'orderpoint_id', 'priority', 'procurement_group_id', 'product_description_variants', 'product_tmpl_id',
            'product_tracking', 'product_uom_category_id', 'product_uom_qty', 'product_variant_attributes',
            'propagate_cancel', 'purchase_order_count', 'rating_ids', 'reservation_state', 'reserve_visible',
            'sale_order_count', 'scrap_count', 'scrap_ids', 'search_date_category', 'show_allocation',
            'show_final_lots', 'show_lock', 'show_lot_ids', 'show_produce', 'show_produce_all', 'show_valuation',
            'unbuild_count', 'unbuild_ids', 'unreserve_visible', 'use_create_components_lots', 'valid_product_template_attribute_line_ids',
            'website_message_ids', 'activity_ids', 'activity_state', 'activity_type_id', 'activity_user_id',
            'activity_date_deadline', 'activity_summary', 'activity_type_icon', 'activity_exception_icon',
            'activity_exception_decoration', 'activity_calendar_event_id', 'all_move_ids', 'all_move_raw_ids',
            'allow_workorder_dependencies', 'backorder_sequence', 'components_availability', 'consumption',
            'finished_move_line_ids', 'move_dest_ids', 'move_raw_ids', 'move_finished_ids', 'move_byproduct_ids',
            'origin', 'priority', 'product_id', 'product_qty', 'product_uom_id', 'qty_produced', 'qty_producing',
            'state', 'user_id', 'warehouse_id', 'workorder_ids'
        ]
    if workorder_fields is None:
        workorder_fields = [
            'id', 'name', 'state', 'production_id', 'workcenter_id', 'operation_id', 'date_start', 'date_finished',
            'duration', 'duration_expected', 'duration_percent', 'duration_unit', 'progress', 'qty_produced',
            'qty_producing', 'qty_production', 'qty_remaining', 'qty_reported_from_previous_wo', 'sequence',
            'is_planned', 'is_produced', 'is_user_working', 'working_user_ids', 'last_working_user_id',
            'allow_workorder_dependencies', 'barcode', 'blocked_by_workorder_ids', 'company_id', 'consumption',
            'costs_hour', 'create_date', 'create_uid', 'display_name', 'finished_lot_id', 'has_worksheet',
            'json_popover', 'leave_id', 'mo_analytic_account_line_ids', 'move_finished_ids', 'move_line_ids',
            'move_raw_ids', 'needed_by_workorder_ids', 'operation_note', 'product_id', 'product_tracking',
            'product_uom_id', 'production_availability', 'production_bom_id', 'production_date', 'production_state',
            'scrap_count', 'scrap_ids', 'show_json_popover', 'time_ids', 'wc_analytic_account_line_ids',
            'workcenter_id', 'working_state', 'worksheet', 'worksheet_google_slide', 'worksheet_type', 'write_date', 'write_uid'
        ]
    if user_fields is None:
        user_fields = ['id', 'name', 'login', 'email', 'company_id', 'active']
    uid, _, models = odoo_login()
    productions = models.execute_kw(DB_NAME, uid, PASSWORD, 'mrp.production', 'read', [[production_id], fields])
    if not productions:
        return None
    production = productions[0]
    # Lấy danh sách công đoạn (workorder)
    workorder_ids = production.get('workorder_ids', [])
    workorders = []
    if workorder_ids:
        workorders = models.execute_kw(DB_NAME, uid, PASSWORD, 'mrp.workorder', 'read', [workorder_ids, workorder_fields])
        # Lấy chi tiết user đang tham gia công đoạn
        for wo in workorders:
            user_ids = wo.get('working_user_ids', [])
            if user_ids:
                users = models.execute_kw(DB_NAME, uid, PASSWORD, 'res.users', 'read', [user_ids, user_fields])
                wo['working_user_details'] = users
            else:
                wo['working_user_details'] = []
    production['workorders'] = workorders
    return production

def get_all_workcenters(fields=None):
    """
    Lấy danh sách tất cả khu vực sản xuất (mrp.workcenter) trong hệ thống.
    Trả về list các workcenter, [] nếu không có.
    """
    if fields is None:
        fields = [
            'id', 'name', 'active', 'code', 'company_id', 'display_name', 'note', 'sequence', 'color',
            'resource_id', 'resource_calendar_id', 'working_state', 'workorder_count', 'workorder_late_count',
            'workorder_pending_count', 'workorder_progress_count', 'workorder_ready_count', 'workcenter_load',
            'performance', 'time_efficiency', 'productive_time', 'blocked_time', 'costs_hour', 'default_capacity',
            'alternative_workcenter_ids', 'capacity_ids', 'expense_account_id', 'currency_id', 'analytic_distribution',
            'analytic_precision', 'distribution_analytic_account_ids', 'costs_hour_account_ids', 'order_ids',
            'rating_ids', 'tag_ids', 'routing_line_ids', 'time_ids', 'kanban_dashboard_graph', 'tz', 'has_message',
            'has_routing_lines', 'message_attachment_count', 'message_follower_ids', 'message_has_error',
            'message_has_error_counter', 'message_has_sms_error', 'message_ids', 'message_is_follower',
            'message_needaction', 'message_needaction_counter', 'message_partner_ids', 'website_message_ids',
            'create_date', 'create_uid', 'write_date', 'write_uid', 'oee', 'oee_target'
        ]
    uid, _, models = odoo_login()
    workcenter_ids = models.execute_kw(DB_NAME, uid, PASSWORD, 'mrp.workcenter', 'search', [[]])
    if not workcenter_ids:
        return []
    workcenters = models.execute_kw(DB_NAME, uid, PASSWORD, 'mrp.workcenter', 'read', [workcenter_ids, fields])
    return workcenters
# Biến global lưu cache danh sách công đoạn theo workcenter_id
WORKCENTER_WORKORDERS_CACHE = {}

def get_workorders_by_workcenter(workcenter_id, fields=None):
    """
    Lấy danh sách các công đoạn (mrp.workorder) theo workcenter_id.
    Trả về list các workorder, [] nếu không có.
    """
    if fields is None:
        fields = [
            'id', 'name', 'state', 'production_id', 'workcenter_id', 'operation_id', 'date_start', 'date_finished',
            'duration', 'duration_expected', 'duration_percent', 'duration_unit', 'progress', 'qty_produced',
            'qty_producing', 'qty_production', 'qty_remaining', 'qty_reported_from_previous_wo', 'sequence',
            'is_planned', 'is_produced', 'is_user_working', 'working_user_ids', 'last_working_user_id',
            'allow_workorder_dependencies', 'barcode', 'blocked_by_workorder_ids', 'company_id', 'consumption',
            'costs_hour', 'create_date', 'create_uid', 'display_name', 'finished_lot_id', 'has_worksheet',
            'json_popover', 'leave_id', 'mo_analytic_account_line_ids', 'move_finished_ids', 'move_line_ids',
            'move_raw_ids', 'needed_by_workorder_ids', 'operation_note', 'product_id', 'product_tracking',
            'product_uom_id', 'production_availability', 'production_bom_id', 'production_date', 'production_state',
            'scrap_count', 'scrap_ids', 'show_json_popover', 'time_ids', 'wc_analytic_account_line_ids',
            'workcenter_id', 'working_state', 'worksheet', 'worksheet_google_slide', 'worksheet_type', 'write_date', 'write_uid'
        ]
    uid, _, models = odoo_login()
    domain = [['workcenter_id', '=', workcenter_id]]
    workorder_ids = models.execute_kw(DB_NAME, uid, PASSWORD, 'mrp.workorder', 'search', [domain])
    workorders = models.execute_kw(DB_NAME, uid, PASSWORD, 'mrp.workorder', 'read', [workorder_ids, fields])
    return workorders

def export_all_employees_with_qr(output_dir="employee_qr_export"):
    """
    Lấy danh sách tất cả nhân viên, lấy detail từng nhân viên (có user_detail), tạo QR code cho từng nhân viên,
    xuất ra file (1 file cho mỗi nhân viên, gồm thông tin nhân viên và QR code).
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    employees = get_all_employees()
    for emp in employees:
        emp_detail = get_employee_by_id(emp['id'])
        # Tạo file thông tin nhân viên
        info_lines = [
            f"ID: {emp_detail.get('id')}",
            f"Tên: {emp_detail.get('name')}",
            f"Email: {emp_detail.get('work_email', '')}",
            f"Điện thoại: {emp_detail.get('work_phone', '')}",
            f"Chức vụ: {emp_detail.get('job_title', '')}",
            f"Phòng ban: {emp_detail.get('department_id', '')}",
        ]
        user_detail = emp_detail.get('user_detail')
        if user_detail:
            info_lines.append("--- User Detail ---")
            info_lines.append(f"User ID: {user_detail.get('id')}")
            info_lines.append(f"User Name: {user_detail.get('name')}")
            info_lines.append(f"Login: {user_detail.get('login')}")
            info_lines.append(f"Email: {user_detail.get('email')}")
            info_lines.append(f"Company: {user_detail.get('company_id')}")
            
            # Chỉ tạo QR code khi có user_detail
            qr_data = json.dumps(emp_detail, ensure_ascii=False)
            qr = qrcode.make(qr_data)
            # Lưu QR code
            qr_path = os.path.join(output_dir, f"employee_{emp_detail['id']}_qr.png")
            qr.save(qr_path)
            info_text = "\n".join(info_lines)
            # Lưu file text
            info_path = os.path.join(output_dir, f"employee_{emp_detail['id']}.txt")
            with open(info_path, "w", encoding="utf-8") as f:
                f.write(info_text)
        
    

def add_users_to_workorder(workorder, user_ids):
    """
    Tạo mới record productivity cho từng user trên công đoạn (workorder).
    Truyền đủ các trường production_id, workcenter_id, user_id, loss_type.
    Trả về danh sách ID record đã tạo.
    """
    if not workorder or not user_ids:
        print("❌ Thiếu workorder object hoặc danh sách user_ids!")
        return []

    def extract_id(val):
        return val[0] if isinstance(val, list) else val

    production_id = extract_id(workorder.get('production_id'))
    workcenter_id = extract_id(workorder.get('workcenter_id'))
    company_id    = extract_id(workorder.get('company_id'))
    workorder_id  = workorder.get('id')

    if not all([production_id, workcenter_id, workorder_id]):
        print("❌ Workorder thiếu thông tin bắt buộc (production_id/workcenter_id/workorder_id)")
        return []

    uid, _, models = odoo_login()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    created_ids = []

    for user_id in user_ids:
        vals = {
            'production_id': production_id,
            'workcenter_id': workcenter_id,
            'company_id': company_id,
            'workorder_id': workorder_id,
            'user_id': user_id,
            'date_start': now,
            'loss_id': 7,
            'description': f"Tự động gán công nhân {user_id}"
        }
        try:
            record_id = models.execute_kw(
                DB_NAME, uid, PASSWORD,
                'mrp.workcenter.productivity', 'create',
                [vals]
            )
            created_ids.append(record_id)
            print(f"✅ Đã tạo productivity cho user {user_id} trên workorder {workorder_id}, id={record_id}")
        except Exception as e:
            print(f"❌ Lỗi khi tạo productivity cho user {user_id}: {e}")

    print(f"🔄 Tổng cộng đã tạo {len(created_ids)} record productivity cho workorder {workorder_id}")
    return created_ids