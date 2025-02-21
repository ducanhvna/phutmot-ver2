import xmlrpc.client
import pandas as pd
from datetime import datetime, timezone, timedelta
from minio import Minio
from minio.error import S3Error

# Kết nối tới server Odoo
ODOO_BASE_URL = "https://hrm.mandalahotel.com.vn"
ODOO_DB = "apechrm_product_v3"
ODOO_USERNAME = "admin_ho"
ODOO_PASSWORD = "43a824d3a724da2b59d059d909f13ba0c38fcb82"

# Kết nối tới Minio
client = Minio(
    "42.113.122.201:9000",
    access_key="FLoU4kYrt6EQ8eyWBLjD",
    secret_key="LBa3KybNAxwxHWuFPqKF00ppIi5iOotJXQQzriUa",
    secure=False  # Đặt thành True nếu bạn sử dụng HTTPS
)

# Xác thực người dùng Odoo
common = xmlrpc.client.ServerProxy(f'{ODOO_BASE_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})

# Kết nối tới object trên Odoo
models = xmlrpc.client.ServerProxy(f'{ODOO_BASE_URL}/xmlrpc/2/object')

# Số lượng phần tử trong mỗi trang
limit = 100
offset = 0
all_records = []

# Lặp qua các trang dữ liệu
while True:
    # Lấy dữ liệu với phân trang
    allocation_records = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'hr.employee.allocation.v2', 'search_read',
        [[]],  # Điều kiện lọc
        {'fields': ['id', 'new_company_working_date', 'new_job_id_date', 'new_department_working_date', 
                    'severance_day_old_company',
                    'current_shift', 'new_shift', 'day_change_shift',
                    "date_end_shift", "company_id", "contract_name", "date_end", "date_sign",
                    "contract_type_id", "employee_ids", "employee_name", "employee_code"], 'limit': limit, 'offset': offset}
    )
    
    # Nếu không còn dữ liệu, thoát vòng lặp
    if not allocation_records:
        break
    
    # Thêm dữ liệu vào danh sách all_records
    all_records.extend(allocation_records)

    # Tăng offset lên để lấy trang tiếp theo
    offset += limit

# Chuyển đổi danh sách thành DataFrame của pandas
df_all_records = pd.DataFrame(all_records)

# Giải nén employee_ids thành các hàng riêng biệt
df_all_records = df_all_records.explode('employee_ids')

# Lấy danh sách employee_ids unique
employee_ids = df_all_records['employee_ids'].unique().tolist()

# Lấy thông tin employee từ server Odoo
employee_data = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'hr.employee', 'search_read',
    [[['id', 'in', employee_ids]]],
    {'fields': ['id', 'name', 'code']}
)

# Chuyển employee_data thành DataFrame
df_employees = pd.DataFrame(employee_data)

# Merge dữ liệu employee vào allocation records
df_merged = pd.merge(df_all_records, df_employees, how='left', left_on='employee_ids', right_on='id', suffixes=('', '_employee'))

# Lưu dữ liệu vào file Excel
df_merged.to_excel('merged_allocation_records.xlsx', index=False)

print("Dữ liệu đã được lưu vào file 'merged_allocation_records.xlsx'")
