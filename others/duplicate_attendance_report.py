import xmlrpc.client
from datetime import datetime
import pandas as pd
# Odoo connection details
ODOO_BASE_URL = "https://hrm.mandalahotel.com.vn"
ODOO_DB = "apechrm_product_v3"
ODOO_USERNAME = "admin_ho"
ODOO_PASSWORD = "43a824d3a724da2b59d059d909f13ba0c38fcb82"

# Connect to Odoo
common = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/common")
uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/object")

# Define the start and end dates for January 2025
start_date = datetime.strptime("2025-04-01", "%Y-%m-%d")
end_date = datetime.strptime("2025-04-30", "%Y-%m-%d")

# Search for attendance records within the date range
attendance_records = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
    'hr.apec.attendance.report', 'search_read',
    [[('date', '>=', start_date), ('date', '<=', end_date)]],
    {'fields': ['id', 'employee_code', 'company', 'employee_name', 'date', 'total_work_time'], 'order': 'id ASC'})

# Create a dictionary to store the optimal record for each (employee_code, company, date)
max_work_time_records = {}

for record in attendance_records:
    key = (record['employee_code'], record['company'], record['date'])
    
    if key not in max_work_time_records:
        max_work_time_records[key] = record
    else:
        # Prioritize the record with the highest total_work_time
        if record['total_work_time'] > max_work_time_records[key]['total_work_time']:
            max_work_time_records[key] = record
        elif record['total_work_time'] == max_work_time_records[key]['total_work_time']:
            # If total_work_time is the same, choose the record with the highest ID
            if record['id'] > max_work_time_records[key]['id']:
                max_work_time_records[key] = record

# Identify valid records to keep
valid_ids = {record['id'] for record in max_work_time_records.values()}
# Collect records to be deleted
invalid_records = [record for record in attendance_records if record['id'] not in valid_ids]

# Save invalid records to invalid.xlsx
df = pd.DataFrame(invalid_records)
df.to_excel("invalid.xlsx", index=False)
print("Invalid records saved to invalid.xlsx")

# Delete duplicate records (keeping only the optimal ones)
for record in attendance_records:
    if record['id'] not in valid_ids:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.apec.attendance.report', 'unlink', [[record['id']]])
        print(f'unlink {record}')

print("Duplicates removed successfully with optimized selection.")

# # Odoo connection details
# ODOO_BASE_URL = "https://hrm.mandalahotel.com.vn"
# ODOO_DB = "apechrm_product_v3"
# ODOO_USERNAME = "admin_ho"
# ODOO_PASSWORD = "43a824d3a724da2b59d059d909f13ba0c38fcb82"

# # Connect to Odoo
# common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(ODOO_BASE_URL))
# uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
# models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(ODOO_BASE_URL))

# # Define the start and end dates for December 2024
# start_date = datetime.strptime("2025-01-01", "%Y-%m-%d")
# end_date = datetime.strptime("2025-01-31", "%Y-%m-%d")

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
