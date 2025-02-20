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
file_path = "QUỸ NGHỈ -2024.xlsx"
sheet_name = "CL -2024"  # Change this to your actual sheet name

# Read the Excel file, specifying the header row
df = pd.read_excel(file_path, sheet_name=sheet_name, header=[0,1])
print(df.columns)
print(df[("CL-2024", 10)])
# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    employee_name = row[df.columns[1]]
    
    if pd.notnull(employee_name):
        # Search for the employee record in Odoo
        search_domain = [
            ('company_id', '=', 18),
            ('employee_name', '=', employee_name),
            ('date_calculate', '=', '2025-02-01')
        ]
        employee_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.cl.report', 'search', [search_domain])

        if employee_ids:
            # Update the 'november' field for the found record
            update_values = {'increase_probationary_10': 0,
                             'increase_official_10': 0,
                             'used_probationary_10': 0,
                             'used_official_10': 0 if pd.isna(row[("CL-2024", 10)]) or pd.isnull(row[("CL-2024", 10)]) else row[("CL-2024", 10)],
                             'overtime_probationary_10': 0,
                             'overtime_official_10': 0,}
            models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.cl.report', 'write', [employee_ids, update_values])

print("Update process completed.")
