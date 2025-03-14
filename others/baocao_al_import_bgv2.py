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
file_path = "baocao_al_import_bgv2.xlsx"
sheet_name = "AL"  # Change this to your actual sheet name

# Read the Excel file, specifying the header row
df = pd.read_excel(file_path, sheet_name=sheet_name, header=[0,1])
print(df.columns)

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    employee_code = row[df.columns[1]]
    
    if pd.notnull(employee_code):
        # Search for the employee record in Odoo
        search_domain = [
            ('company_id', '=', 8),
            ('employee_code', '=', employee_code),
            ('date_calculate_leave', '=', '2025-03-01')
        ]
        employee_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.al.report', 'search', [search_domain])

        if employee_ids:
            # Update the 'november' field for the found record
            update_values = {'remaining_leave': 0 if pd.isna(row[df.columns[28]]) or pd.isnull(row[df.columns[28]]) else row[df.columns[28]]}
            models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.al.report', 'write', [employee_ids, update_values])
            print(f'updated {employee_ids}-{update_values}')
print("Update process completed.")
