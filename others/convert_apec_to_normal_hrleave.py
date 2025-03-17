import xmlrpc.client
# Kết nối tới server Odoo
ODOO_BASE_URL = "https://hrm.mandalahotel.com.vn"
ODOO_DB = "apechrm_product_v3"
ODOO_USERNAME = "admin_ho"
ODOO_PASSWORD = "43a824d3a724da2b59d059d909f13ba0c38fcb82"

hrleave_fields = [
    "id",
    "employee_id",
    "employee_code",
    "employee_company_id",
    "active",
    "holiday_status_id",
    "minutes",
    "time",
    "state",
    "request_date_from",
    "request_date_to",
    "attendance_missing_from",
    "attendance_missing_to",
    "reasons",
    "for_reasons",
    "convert_overtime",
    "employee_company_id",
    "multiplier_work_time",
    "overtime_from",
    "overtime_to",
    "write_date",
    "multiplier_wage",
    "multiplied_wage_amount",
    "multiplied_work_time_amount",
    "absent_morning",
    "absent_afternoon",
]

def download_data(models, db, uid, password, model_name, fields, start_str, end_str):
    LIMIT_SIZE = 300
    index = 0
    len_data = 0
    merged_array = []
    if model_name == 'hr.leave':
        domain = [[
            ("request_date_to", ">=", start_str),
            ("request_date_from", "<=", end_str),
            ("active", "=", True),
            ("state", "=", "validate"),
        ]]
    else:
        raise ValueError("Invalid model name")

    while (len_data == LIMIT_SIZE) or (index == 0):
        ids = models.execute_kw(
            db,
            uid,
            password,
            model_name,
            'search',
            domain,
            {'offset': index * LIMIT_SIZE, 'limit': LIMIT_SIZE},
        )
        len_data = len(ids)
        print(f"{model_name} length: {len_data}")
        merged_array = list(set(merged_array) | set(ids))
        index += 1

    # Split ids into chunks of 200
    ids_chunks = [merged_array[i:i + 200] for i in range(0, len(merged_array), 200)]
    print("chunks: ", len(ids_chunks))
    merged_data = []

    for ids_chunk in ids_chunks:
        # Fetch data from Odoo
        data_chunk = models.execute_kw(
            db,
            uid,
            password,
            model_name,
            'read',
            [ids_chunk],
            {'fields': fields},
        )
        merged_data.extend(data_chunk)

    return merged_data
def download_hr_leave():
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(ODOO_BASE_URL))
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(ODOO_BASE_URL))
    hr_leave_data = download_data(models, ODOO_DB, uid, ODOO_PASSWORD, 'hr.leave', hrleave_fields, '2025-01-01', '2025-01-31')
    print(hr_leave_data)

# download_hr_leave()

def get_leave_data(url, db, username, password):
    try:
        # Kết nối đến Odoo
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
        uid = common.authenticate(db, username, password, {})
        if not uid:
            return "Authentication failed. Please check your credentials."

        models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

        # Truy vấn dữ liệu từ hr.leave
        leave_data = models.execute_kw(
            db, uid, password,
            'hr.leave', 'search_read',
            [[['state', '=', 'validate']]],  # Lọc các yêu cầu nghỉ phép đã phê duyệt
            {'fields': ['holiday_status_id', 'number_of_days', 'number_of_days_display', 'employee_id']}
        )

        # Truy vấn thêm dữ liệu số ngày được cấp phát (nếu cần)
        allocation_data = models.execute_kw(
            db, uid, password,
            'hr.leave.allocation', 'search_read',
            [[]],  # Bạn có thể thêm bộ lọc ở đây nếu cần
            {'fields': ['holiday_status_id', 'number_of_days', 'employee_id']}
        )

        # Tạo danh sách kết quả
        results = []
        for leave in leave_data:
            allocation = next(
                (alloc for alloc in allocation_data if alloc['holiday_status_id'][0] == leave['holiday_status_id'][0] 
                 and alloc['employee_id'][0] == leave['employee_id'][0]), None
            )
            
            results.append({
                "Loại nghỉ phép": leave['holiday_status_id'][1],
                "Số ngày còn lại": leave['number_of_days'],
                "Số ngày đã sử dụng": leave.get('number_of_days_display', 0),
                "Số ngày được cấp phát": allocation['number_of_days'] if allocation else "Không có dữ liệu",
                "Nhân viên": leave['employee_id'][1]
            })

        return results

    except Exception as e:
        return f"An error occurred: {e}"

# Sử dụng function
url = "https://admin.hinosoft.com"
db = "odoo"
username = "admin"
password = "admin"  # Hãy thay thế bằng mật khẩu thực tế

leave_info = get_leave_data(url, db, username, password)
print(leave_info)
