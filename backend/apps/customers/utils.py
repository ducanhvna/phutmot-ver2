import json
import requests

# Thông tin kết nối
url = "https://solienlacdientu.info/jsonrpc"  # Thay bằng địa chỉ Odoo của bạn
db = "goldsun"
username = "admin"
password = "admin"

# Bước 1: Đăng nhập để lấy uid
def authenticate():
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "common",
            "method": "login",
            "args": [db, username, password]
        },
        "id": 1
    }
    response = requests.post(url, json=payload).json()
    return response["result"]

uid = authenticate()

# Bước 2: Tạo partner với số điện thoại
def create_partner(name, phone):
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                db,
                uid,
                password,
                "res.partner",
                "create",
                [{
                    "name": name,
                    "phone": phone,
                    "customer_rank": 1
                }]
            ]
        },
        "id": 2
    }
    response = requests.post(url, json=payload).json()
    return response["result"]

def search_partner_by_mobile(mobile_number):
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                db,
                uid,
                password,
                "res.partner",
                "search_read",
                [[["phone", "=", mobile_number]]],  # Điều kiện tìm kiếm
                {
                    "fields": ["id", "name", "phone", "mobile", "email"],  # Trường cần lấy
                    "limit": 5  # Giới hạn số kết quả
                }
            ]
        },
        "id": 3
    }
    response = requests.post(url, json=payload).json()
    return response["result"]

# # Ví dụ sử dụng
# results = search_partner_by_mobile("+84 912 345 678")
# print("Kết quả tìm kiếm partner theo số điện thoại:", results)
# for partner in results:
#     print(f"ID: {partner['id']}, Tên: {partner['name']}, Mobile: {partner['mobile']}, Phone: {partner['phone']}, Email: {partner.get('email', 'Không có')}")
# # Tạo partner mới
# partner_id = create_partner("Công ty ABC", "+84 912 345 678")
# print(f"Đã tạo partner với ID: {partner_id}")