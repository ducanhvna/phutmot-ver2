import xmlrpc.client
url = "https://admin.hinosoft.com"
db = "odoo"
admin_username = "demo"
admin_api_key = "ff59f8f9-9e09-4aa4-9d72-bcb5da33f0f0"
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, admin_username, admin_api_key, {})
print(uid)

# Cấu hình thông tin kết nối
url = "https://hrm.mandalahotel.com.vn"
db = "apechrm_product_v3"
admin_username = "admin_mn"
admin_api_key = "hrmn@123"

# Kết nối và xác thực admin
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, admin_username, admin_api_key, {})

if uid:
    # Kết nối đến object
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

    # Lấy ID của user mà bạn muốn tạo API key
    user_id = models.execute_kw(
        db, uid, admin_api_key, 'res.users', 'search', [[('login', '=', 'admin_mn')]]
    )[0]

    # Tạo API key cho user
    api_key_data = {
        'user_id': user_id,
        'name': 'My API Key',
    }
    print(api_key_data)
    new_api_key_id = models.execute_kw(
        db, uid, admin_api_key, 'res.users.apikeys', 'create', [api_key_data]
    )

    print(f"API Key được tạo với ID: {new_api_key_id}")
else:
    print("Xác thực thất bại!")
