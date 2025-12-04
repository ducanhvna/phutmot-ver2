import requests
import json

# Data nhận được
data = {
    "id": 1,
    "displayName": "An Phương Loan",
    "phone": "*0819322222",
    "email": "",
    "street": "51 nguyễn công trứ , đồng nhân , hai bà trưng , hà nội",
    "city": None,
    "stateId": 0,
    "vat": None,
    "cccdNumber": None,
    "cccdVerified": 0,
    "customerType": "CustomerType.newCustomer",
    "sellorderitems": [
        {
            "id": 21,
            "name": "Nhẫn ép vỉ Vàng Rồng Thăng Long, 1 chỉ - 24K (999.9)",
            "quantity": 3,
            "price_unit": 1000000.0,
            "total_price_with_tax": 3000000.0
        },
        {
            "id": 22,
            "name": "Nhẫn tròn ép vỉ Kim Gia Bảo, loại 0.5 chỉ - 24K (999.9)",
            "quantity": 1,
            "price_unit": 7425000.0,
            "total_price_with_tax": 7425000.0
        },
        {
            "id": 24,
            "name": "Nhẫn ép vỉ Vàng Rổng Thăng Long , 5 chỉ - 24K (999.9)",
            "quantity": 4,
            "price_unit": 1000000.0,
            "total_price_with_tax": 4000000.0
        }
    ]
}

# URL API
url = "http://192.168.0.223:8869/api/public/updatedatehang"

# Header
headers = {
    "Content-Type": "application/json; charset=utf-8"
}

# Lấy mã khách hàng từ phone (bỏ dấu *)
ma_khachhang = data["phone"].replace("*", "")

# Ghép payload
payload = {
    "ma_khachhang":"0969682985",
    "manhanvien":"0919933911",
    "dien_giai":"",
    "danh_sach":[{
        "mahang":"24BTV49KD0-307060-0002",
    "soluong":1
    }]
}


print(payload)
# Gọi API POST
response = requests.post(url, headers=headers, data=json.dumps(payload))

# In kết quả
print("Status code:", response.status_code)
print("Response body:", response.text)