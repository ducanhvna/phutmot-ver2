import requests
import json
import os

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
    "sellorderitems": []
}

BASE_URL = os.environ.get("INTERNAL_API_BASE", "http://118.70.146.150:8869")

# URL API
search_url = f"{BASE_URL}/api/public/khach_hang/timkiem"
# Header
headers = {
    "Content-Type": "application/json; charset=utf-8"
}

# Lấy mã khách hàng từ phone (bỏ dấu *)
ma_khachhang = data["phone"].replace("*", "")

# Ghép payload
payload = {
     "sdt": "0969682985" # số điện thoại hoặc căn cước
}


print(payload)
# Gọi API POST
response = requests.post(search_url, headers=headers, data=json.dumps(payload))

# In kết quả
print("Status code:", response.status_code)
print("Response body:", response.text)

