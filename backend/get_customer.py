
import requests

url = "https://14.224.192.52:9999/api/v1/calculate-price"

# Nếu bạn cần gửi payload (JSON, form...), ví dụ:
CLIENT_CERT_PATH = "data/Product/client_cert.pem"
CLIENT_KEY_PATH = "data/Product/client_key.pem"
CA_CERT_PATH = "data/Product/ca_cert.pem"  # Nếu cần xác thực server
# Đường dẫn tới file chứng chỉ và key
cert = (CLIENT_CERT_PATH, CLIENT_KEY_PATH)
# Nếu server dùng self-signed cert, bạn có thể cần ca-cert.pem hoặc tắt verify (không khuyến nghị cho production)
# call api  GET "http://localhost:9897/api/v1/products/summary"

response = requests.post(
    "https://14.224.192.52:9999/api/v1/generate-qr",
    json={
        "account_type": "1",
        "account_no": "00045627001",
        "amount": "10000",
        "add_info": "Thanh toan hoa don"
    },
    cert=cert,
    verify= CA_CERT_PATH # hoặc verify=False nếu chỉ test
)
print(response.status_code)
qr = response.json()
print(qr)

url = "https://14.224.192.52:9999/api/v1/products/summary"
response = requests.get(
    url,
    cert=cert,
    verify= CA_CERT_PATH # hoặc verify=False nếu chỉ test
)
print(response.status_code)
tygia = response.json()
print(tygia)

total_products = tygia['total_products']
page_size = 50
numberof_pages = (total_products + page_size - 1) # page_size  # Làm tròn lên

# POST list /api/v1/products/list
# url = "https://14.224.192.52:9999/api/v1/products/list"
# for page in range(1, numberof_pages + 1):
#     response = requests.post(
#         url,
#         json={
#                 "page": page,
#                 "page_size": page_size,
#                 "search": ""  # Optional - tìm kiếm theo mã hoặc tên sản phẩm
#             },
#         cert=cert,
#         verify= CA_CERT_PATH # hoặc verify=False nếu chỉ test
#     )

#     print(response.status_code)
#     products = response.json()
#     print(products)