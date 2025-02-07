import xmlrpc.client
from datetime import datetime

# Odoo connection details
ODOO_BASE_URL = "https://hrm.mandalahotel.com.vn"
ODOO_DB = "apechrm_product_v3"
ODOO_USERNAME = "admin_ho"
ODOO_PASSWORD = "43a824d3a724da2b59d059d909f13ba0c38fcb82"

# Connect to Odoo
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(ODOO_BASE_URL))
uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(ODOO_BASE_URL))

# Define the start and end dates for December 2024
start_date = datetime.strptime("2025-01-01", "%Y-%m-%d")
end_date = datetime.strptime("2025-01-31", "%Y-%m-%d")

# Search for attendance records within the date range
attendance_records = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
    'hr.apec.attendance.report', 'search_read',
    [[('date', '>=', start_date), ('date', '<=', end_date)]],
    {'fields': ['id', 'employee_code', 'company', 'date'], 'order': 'id ASC'})

# Create a dictionary to store the highest id for each (employee_code, company, date) combination
highest_ids = {}
for record in attendance_records:
    key = (record['employee_code'], record['company'], record['date'])
    if key not in highest_ids or record['id'] > highest_ids[key]:
        highest_ids[key] = record['id']

# Delete records that are duplicates (keep only the record with the highest id)
for record in attendance_records:
    key = (record['employee_code'], record['company'], record['date'])
    if record['id'] != highest_ids[key]:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.apec.attendance.report', 'unlink', [[record['id']]])
        print(f'unlink {record}')

print("Duplicates removed successfully.")
