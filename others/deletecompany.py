import xmlrpc.client

# Cấu hình kết nối
url = "https://hrm.mandalahotel.com.vn"
db = "apechrm_product_v3"
username = "admin_ho"
password = "43a824d3a724da2b59d059d909f13ba0c38fcb82"

# Kết nối đến server
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})

# Tạo kết nối đến object
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

# ID của công ty bạn muốn xóa và ID của công ty giữ chỗ
company_id = 36  # Thay thế bằng ID của công ty bạn muốn xóa
placeholder_company_id = 2  # Thay thế bằng ID của công ty giữ chỗ

# Function to archive records
def archive_records(model, field, company_id):
    try:
        ids = models.execute_kw(db, uid, password, model, 'search', [[(field, '=', company_id)]])
        if ids:
            models.execute_kw(db, uid, password, model, 'write', [ids, {'active': False}])
            print(f"Archived records in model {model}.")
    except xmlrpc.client.Fault as e:
        print(f"Failed to archive records in model {model}: {e}")

# Archive stock.picking.type records
archive_records('stock.picking.type', 'company_id', company_id)

# Reassign records in hr.upload.attendance by adjusting month and year
def increment_month_year(year, month):
    if month == 12:
        return year + 1, 1
    else:
        return year, month + 1

current_year, current_month = 2026, 1

def reassign_until_successful_with_int_month(model, field, company_id, placeholder_company_id):
    global current_year, current_month
    while True:
        try:
            ids = models.execute_kw(db, uid, password, model, 'search', [[(field, '=', company_id)]])
            if ids:
                models.execute_kw(db, uid, password, model, 'write', [ids, {field: placeholder_company_id, 'month': current_year * 100 + current_month}])
                print(f"Successfully reassigned records in model {model} to placeholder company with date {current_year}-{current_month:02d}.")
                break  # Exit the loop when successful
            else:
                break  # No records to update
        except xmlrpc.client.Fault as e:
            print(f"Retrying reassignment for model {model} with date {current_year}-{current_month:02d}: {e}")
            current_year, current_month = increment_month_year(current_year, current_month)

# Reassign hr.upload.attendance records to placeholder company with date increment
reassign_until_successful_with_int_month('hr.upload.attendance', 'company_id', company_id, placeholder_company_id)

# Function to delete the company
def delete_company(company_id):
    try:
        models.execute_kw(db, uid, password, 'res.company', 'unlink', [[company_id]])
        print("Company deleted successfully.")
    except xmlrpc.client.Fault as e:
        print(f"Failed to delete company: {e}")

# Reassign records in other models to placeholder company
models_to_update = [
    ('stock.picking.type', 'company_id'),
    # Thêm các model khác nếu cần thiết
]

# Reassign all related records to placeholder company
for model, field in models_to_update:
    reassign_until_successful_with_int_month(model, field, company_id, placeholder_company_id)
    print(model)

# Delete the company
delete_company(company_id)
