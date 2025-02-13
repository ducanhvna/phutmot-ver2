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

# Load the Excel file
file_path = "Báo cáo tổng hợp chấm công 11.2024.xlsx"
sheet_name = "CL"  # Change this to your actual sheet name

# Read the Excel file, specifying the header row
df = pd.read_excel(file_path, sheet_name=sheet_name, header=[0,1,2])
print(df.columns)
print(df[(      'Tháng 11',    'Phát sinh tăng',            'Thử việc')])
# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    employee_code = row[(    'Mã nhân sự',        'Mã nhân sự',          'Mã nhân sự')]
    
    if pd.notnull(employee_code):
        # Search for the employee record in Odoo
        search_domain = [
            ('employee_code', '=', employee_code),
            ('date_calculate', '=', '2025-02-01')
        ]
        employee_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.cl.report', 'search', [search_domain])

        if employee_ids:
            # Update the 'november' field for the found record
            update_values = {'increase_probationary_11': row[(      'Tháng 11',    'Phát sinh tăng',            'Thử việc')],
                             'increase_official_11': row[(      'Tháng 11',    'Phát sinh tăng',            'Chính thức')],
                             'used_probationary_11': row[(      'Tháng 11',    'Sử dụng',            'Thử việc')],
                             'used_official_11': row[(      'Tháng 11',    'Sử dụng',            'Chính thức')],
                             'overtime_probationary_11': row[(      'Tháng 11',    'Tăng ca',            'Thử việc')],
                             'overtime_official_11': row[(      'Tháng 11',    'Tăng ca',            'Chính thức')],}
            models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.cl.report', 'write', [employee_ids, update_values])

print("Update process completed.")
