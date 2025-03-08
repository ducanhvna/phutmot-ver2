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

employee_fields = [
    "id",
    "name",
    "user_id",
    "employee_ho",
    "part_time_company_id",
    "part_time_department_id",
    "company_id",
    "code",
    "department_id",
    "time_keeping_code",
    "job_title",
    "probationary_contract_termination_date",
    "severance_day",
    "work_phone",
    "mobile_phone",
    "work_email",
    "personal_email",
    "coach_id",
    "parent_id",
    "birthday",
    "employee_type",
    "workingday",
    "probationary_salary_rate",
    "resource_calendar_id",
    "date_sign",
    "level",
    "working_status",
    "write_date",
    "active",
]
def update_company_name(employeeCode, old_company_working_name, new_company_working_name, from_date):
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(ODOO_BASE_URL))
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(ODOO_BASE_URL))
    domain = [[("date", ">=", from_date),
            ("company",'=', old_company_working_name),
            ("employee_code",'=', employeeCode)
        ]]
    report_ids = models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_PASSWORD,
        "hr.apec.attendance.report",
        "search",
        domain,
    )
    try:
        models.execute_kw(
            ODOO_DB,
            uid,
            ODOO_PASSWORD,
            "hr.apec.attendance.report",
            "write",
            [
                report_ids,
                {
                    "company": new_company_working_name,
                },
            ],
        )
        print('update sucess')
    except Exception as ex:
        print(f"UPdate REPORT ACTIVE: {ex}")

    print (report_ids)

update_company_name('APG2240701019', 'Mandala Chăm Bay Mũi Né', 'Công ty Cổ phần Quản lý Vận hành BĐS Mandala', '2025-02-01')
# Connect to
def process_miss_employee(employeeCode, old_company_id, new_company_id, new_department_id):
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(ODOO_BASE_URL))
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(ODOO_BASE_URL))

    # Search for employees with the specified code
    employee_ids = models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_PASSWORD,
        "hr.employee",
        "search",
        [
            [
                "&",
                "&",
                "|",
                ["company_id", "=", new_company_id],
                ["company_id", "=", old_company_id],
                ["code", "=", employeeCode],
                "|",
                ["active", "=", False],
                ["active", "=", True],
            ]
        ],
    )
    print(employee_ids)
    # Retrieve employee records
    employees = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
        'hr.employee', 'read', [employee_ids, employee_fields])

    # Update the 'active' attribute to true
    if employee_ids:
        try:
            models.execute_kw(
                ODOO_DB,
                uid,
                ODOO_PASSWORD,
                "hr.employee",
                "write",
                [
                    employee_ids,
                    {
                        "active": True,
                        "working_status": "working",
                        "company_id": new_company_id,
                        "department_id": new_department_id,
                        'severance_day': False
                    },
                ],
            )
        except Exception as ex:
            print(f"MISS EMPLOYEE ACTIVE: {ex}")

    # Print employee records
    for employee in employees:
        user_ids = models.execute_kw(
            ODOO_DB,
            uid,
            ODOO_PASSWORD,
            "res.users",
            "search",
            [
                [
                    ["email", "=", employee['work_email']],
                    ['login','=', employee['work_email'].split("@")[0]],
                ]
            ],
        )
        print("user: ",user_ids)
        if len(user_ids) == 1:
            users = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                'res.users', 'read', [user_ids, ['user_ids', 'company_ids']])
            if(not new_company_id in users[0]['company_ids']):
                current_company_ids = users[0]['company_ids']

                # Thêm công ty mới vào danh sách company_ids hiện tại
                # updated_company_ids = current_company_ids + [new_company_id]
                comapny_array = [item for item in users[0]['company_ids']]
                print(comapny_array)
                try:
                    models.execute_kw(
                        ODOO_DB,
                        uid,
                        ODOO_PASSWORD,
                        "res.users",
                        "write",
                        [
                            user_ids,
                            {
                                 "company_ids": [(4, new_company_id)],
                            },
                        ],
                    )
                    print ("Update user id company successfuly")
                except Exception as ex:
                    print(f"Uppdate user  ex: {ex}")
            print(users)
        if (employee['user_id']== False) and (employee['work_email'] != False):
            print(f"{user_ids} ==>{ employee}")
            if len(user_ids)==1:
                try:
                    models.execute_kw(
                        ODOO_DB,
                        uid,
                        ODOO_PASSWORD,
                        "hr.employee",
                        "write",
                        [
                            [employee['id']],
                            {
                                "user_id": user_ids[0]
                            },
                        ],
                    )
                    print ("Update user id successfuly")
                except Exception as ex:
                    print(f"Update employee ex: {ex}")
        else:
            print(employee)

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
        [[['new_company_working_date','!=',False],['state', '=', "đã duyệt"]]],  # Điều kiện lọc
        {'fields': ['id','state', 'new_company_working_date', 'new_job_id_date', 'new_department_working_date', 'current_company_id',
                    'allocation_type', 'current_department_id', 'department_id',
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

# Filter records with state 'đã duyệt' and company_id not False
filtered_df = df_merged[
    (df_merged["state"] == "đã duyệt")
    & (df_merged["company_id"] != False)
    & (df_merged["employee_code"] != False)
]

# Initialize a list to store employees that exist in Odoo
existing_employees = []
existing_contracts = []
# Loop through the filtered DataFrame and check if the employee exists in Odoo
for index, row in filtered_df.iterrows():
    employee_code = row['employee_code']
    company_id = row['company_id'][0]  # Assuming company_id is a list-like structure
    
    # Check if the employee exists in Odoo
    existing_employee = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'hr.employee', 'search',
        [[['code', '=', employee_code], ['company_id', '=', company_id]]]
    )
    if row['company_id'] and (row['company_id'][0] == 5):
        update_company_name(employee_code, row['current_company_id'][1], row['company_id'][1], row['new_company_working_date'])
    if existing_employee:
        existing_employees.append(row)
    else:
        print(f"Đơn {row['id']}-{existing_employee} - {employee_code} - {row['name']} {row['current_company_id']} ---> {row['company_id']} not exist")
        print(f"{row['current_department_id']} ---> {row['department_id']}")
        print(f"New contract name: {row}")
    if row['company_id'] and (row['company_id'][0] == 5):
        process_miss_employee(employee_code, row['current_company_id'][0], row['company_id'][0], row['department_id'][0])
    existing_contract = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'hr.contract', 'search',
        [[['employee_code', '=', employee_code], ['company_id', '=', company_id]]]
    )
    
    if existing_contract:
        existing_contract.append(row)
    else:
        print(f"Hợp đồng {row['id']}-{existing_employee} - {employee_code} - {row['name']} - {row['company_id'][1]} not exist")
# Convert the list of existing employees to a DataFrame
existing_employees_df = pd.DataFrame(existing_employees)

# Save the filtered DataFrame to an Excel file
existing_employees_df.to_excel('existing_employees.xlsx', index=False)

print("Dữ liệu đã được lưu vào file 'existing_employees.xlsx'")
