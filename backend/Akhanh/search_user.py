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
    "sellorderitems": []
}

# URL API
search_url = "http://192.168.0.223:8869/api/public/khach_hang/timkiem"
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

