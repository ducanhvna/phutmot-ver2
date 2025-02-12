import xmlrpc.client

# Define constants for Odoo connection
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
# Connect to Odoo
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(ODOO_BASE_URL))
uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(ODOO_BASE_URL))

# Search for employee named "Trần Thị Hồng" (both active and inactive)
employee_name = 'Trần Thị Hồng'
employee_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
    'hr.employee', 'search',
    [[['name', '=', employee_name], ['active', 'in', [True, False]]]])

# Fetch employee details
employee_details = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
    'hr.employee', 'read', [employee_ids, employee_fields])

print(employee_details)

# Update the employee's active status to True

# result = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
#     'hr.employee', 'write', [employee_ids, {'active': True}])
# print("Employee status updated successfully:", result)
