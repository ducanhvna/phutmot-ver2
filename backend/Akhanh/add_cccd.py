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
url = "http://118.70.146.150:8869/api/public/khach_hang/add"

# Header
headers = {
    "Content-Type": "application/json; charset=utf-8"
}

# Lấy mã khách hàng từ phone (bỏ dấu *)
ma_khachhang = data["phone"].replace("*", "")

# Ghép payload
payload = {
    # "ma_khachhang": ma_khachhang,          # chính là phone bỏ *
    # "manhanvien": "0919933911",            # mã nhân viên
    # "dien_giai": "",
    # "ten_khachhang": data["displayName"],
    # "so_dien_thoai": data["phone"],
    # "email": data["email"],
    # "dia_chi": data["street"],
    # "city": data["city"],
    # "stateId": data["stateId"],
    # "vat": data["vat"],
    # "cccdNumber": data["cccdNumber"],
    # "cccdVerified": data["cccdVerified"],
    # "customerType": data["customerType"],
    # "sellorderitems": data["sellorderitems"]
}

payload = {
    "cccd_cmt": "",
    "ho_ten_khach_hang": "",
    "gioi_tinh": "",
	"dia_chi":"",
	"ngay_sinh":"",
	"email":"",
	"tinh":"",
	"quan":"",
	"phuong":"",
	"nguoi_tao":"",
	"dien_thoai":"",
	"dien_thoai_2":"",
	"dien_thoai_3":"",
	"dien_thoai_4":"",
}

# print(payload)
# Gọi API POST
response = requests.post(url, headers=headers, data=json.dumps(payload))

# In kết quả
print("Status code:", response.status_code)
print("Response body:", response.text)

