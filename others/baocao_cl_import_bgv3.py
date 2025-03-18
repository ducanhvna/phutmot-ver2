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
file_path = "Báo cáo tổng hợp chấm công-BG-10-2024.xlsx"
sheet_name = "Summary Time Attendance"  # Change this to your actual sheet name

# Read the Excel file, specifying the header row
df = pd.read_excel(file_path, sheet_name=sheet_name, header=[8, 10, 11])
print(df.columns)
print(df[df.columns[11]])
print(df[df.columns[12]])

print(df[df.columns[22]])
print(df[df.columns[23]])

print(df[df.columns[18]])
print(df[df.columns[32]])
# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    employee_code = row[df.columns[1]]
    
    if pd.notnull(employee_code):
        # Search for the employee record in Odoo
        search_domain = [
            ('company_id', '=', 8),
            ('employee_code', '=', employee_code),
            ('date_calculate', '=', '2025-01-01')
        ]
        employee_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.cl.report', 'search', [search_domain])
        overtime_probation_normal = 0 if pd.isna(row[df.columns[11]]) or pd.isnull(row[df.columns[11]]) else row[df.columns[11]]
        overtime_probation_holiday = 0 if pd.isna(row[df.columns[12]]) or pd.isnull(row[df.columns[12]]) else row[df.columns[12]]
        
        overtime_offical_normal = 0 if pd.isna(row[df.columns[22]]) or pd.isnull(row[df.columns[22]]) else row[df.columns[22]]
        overtime_offical_holiday = 0 if pd.isna(row[df.columns[23]]) or pd.isnull(row[df.columns[23]]) else row[df.columns[23]]
        
        used_offical = 0 if pd.isna(row[df.columns[32]]) or pd.isnull(row[df.columns[32]]) else row[df.columns[32]]
        used_probationary = 0 if pd.isna(row[df.columns[18]]) or pd.isnull(row[df.columns[18]]) else row[df.columns[18]]
        if employee_ids:
            
            # Update the 'november' field for the found record
            update_values = {
                            #  'overtime_probationary_10': overtime_probation_normal + overtime_probation_holiday,
                            #  'overtime_official_10': overtime_offical_normal + overtime_offical_holiday,
                             'used_probationary_10': int(used_probationary*480),
                             'used_official_10': int(used_offical*480)
                             }
            models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'hr.cl.report', 'write', [employee_ids, update_values])
            print(f"{employee_code}-{update_values}")

print("Update process completed.")
