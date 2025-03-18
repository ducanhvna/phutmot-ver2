import pandas as pd
import xmlrpc.client

# Define constants for Odoo connection
ODOO_BASE_URL = "https://hrm.mandalahotel.com.vn"
ODOO_DB = "apechrm_product_v3"
ODOO_USERNAME = "admin_ho"
ODOO_PASSWORD = "43a824d3a724da2b59d059d909f13ba0c38fcb82"

# Connect to Odoo
common = xmlrpc.client.ServerProxy(f'{ODOO_BASE_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_BASE_URL}/xmlrpc/2/object')

# # Load the Excel file
# file_path = "Báo cáo tổng hợp chấm công-BG-10-2024.xlsx"
# sheet_name = "Summary Time Attendance"  # Change this to your actual sheet name
search_domain = [
    ('company_id', '=', 8),
    ('date_calculate', '=', '2025-02-01')
]
fields = ['id', 'employee_code', 'remaining_total_minute']
cl_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.cl.report', 'search', [search_domain])
print(cl_ids)
data_chunk = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'hr.cl.report',
                "read",
                [cl_ids],
                {"fields": fields},
            )
print(data_chunk)

for row in data_chunk:
    employee_code = row['employee_code']
    
    if pd.notnull(employee_code):
        # Search for the employee record in Odoo
        search_domain = [
            ('company_id', '=', 8),
            ('employee_code', '=', employee_code),
            ('date_calculate', '=', '2025-03-01')
        ]
        employee_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.cl.report', 'search', [search_domain])
        if employee_ids:
            
            # Update the 'november' field for the found record
            update_values = {
                            #  'overtime_probationary_10': overtime_probation_normal + overtime_probation_holiday,
                            #  'overtime_official_10': overtime_offical_normal + overtime_offical_holiday,
                             'increase_probationary_1': int(row['remaining_total_minute'])
                             }
            models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.cl.report', 'write', [employee_ids, update_values])
            print(f"{employee_code}-{update_values}")

print("Update process completed.")
