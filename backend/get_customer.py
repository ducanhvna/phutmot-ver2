
import requests
import pandas as pd
import sqlite3

# Load parquet files
df_dmH = pd.read_parquet('data/Product/DmH.parquet')
df_dmQTTG = pd.read_parquet('data/Product/DmQTTG.parquet')
df_dmVBTG = pd.read_parquet('data/Product/DmVbMM.parquet')

CLIENT_CERT_PATH = "data/Product/client_cert.pem"
CLIENT_KEY_PATH = "data/Product/client_key.pem"
CA_CERT_PATH = "data/Product/ca_cert.pem"
cert = (CLIENT_CERT_PATH, CLIENT_KEY_PATH)

url_tygia_k = "https://14.224.192.52:9999/api/v1/tigia"
response = requests.get(
    url_tygia_k, 
    cert=cert,
    verify= CA_CERT_PATH) # hoặc verify=False nếu chỉ test
tygia_k_data = response.json().get('items', [])
print("Tỷ giá K:", tygia_k_data)
print("Tỷ giá K:", tygia_k_data)
rate_9999 = next((item for item in tygia_k_data if 'Vàng nữ trang 999.9' == item['Ten_VBTG']), None)
rate_999 = next((item for item in tygia_k_data if 'Vàng nữ trang 99.9' == item['Ten_VBTG']), None) 
print("Rate 9999:", rate_9999)
exit(1)
order_add_url = "https://14.224.192.52:9999/api/v1/orders/add"

# POST
# Content-type
# Application/json; charset=utf-8
# Request body
# {
#     "mahang":"24BTV49KD0-307060-0002",
#     "soluong":1,
#    "ma_nhanvien": "0919933911"
# }
# response = requests.post(
#     order_add_url,
#     json={
#         "mahang":"KGB1C-001",
#         "soluong":1,
#         "ma_nhanvien": "0919933911"
#     },
#     cert=cert,
#     verify=CA_CERT_PATH
# )
# print("Order add status:", response.status_code)
# if response.status_code == 200:
#     print(response.json())
# else:
#     print("Lưu đơn hàng thất bại.")
# exit(1)
# --- Product detail API ---
product_detail_url = "https://14.224.192.52:9999/api/v1/product-detail"
response = requests.post(
    product_detail_url,
    json={"barcode": "NCCNV10KD0-509017-002"},
    cert=cert,
    verify=CA_CERT_PATH
)
print("Product detail status:", response.status_code)
print(response.json())

# --- Inventory API ---
inventory_by_store_url = "https://14.224.192.52:9999/api/v1/inventory/by-store"

try:
    response = requests.post(
        inventory_by_store_url,
        json={"ma_kho": "CH2"},
        cert=cert,
        verify=CA_CERT_PATH
    )
    print("Inventory status:", response.status_code)
    inventory = response.json()
    print(inventory)

    items = inventory.get("items", [])
    inventory_merge_df = pd.DataFrame(items)

    print(f"Tồn kho mã mẫu trong kho CH2: {len(inventory_merge_df)} bản ghi")

    # Save to sqlite safely
    with sqlite3.connect('data/products_temp.sqlite', timeout=30) as conn:
        inventory_merge_df.to_sql('inventory', conn, if_exists='replace', index=False)

except Exception as e:
    print(f"❌ Lỗi khi gọi API tồn kho: {e}")
    with sqlite3.connect('data/products_temp.sqlite') as conn:
        inventory_merge_df = pd.read_sql("SELECT * FROM inventory", conn)
    print(f"Tồn kho mã mẫu trong kho CH2 từ sqlite: {len(inventory_merge_df)} bản ghi")

# --- Join with DmH ---
final_df = pd.merge(df_dmH, inventory_merge_df, left_on='Ma_Tong', right_on='ma_mau', how='inner')
print(f"Tồn kho mã mẫu trong kho CH2 sau khi join DmH: {len(final_df)} bản ghi")

# Save final result
with sqlite3.connect('data/products_temp.sqlite', timeout=30) as conn:
    final_df.to_sql('inventory_with_details', conn, if_exists='replace', index=False)

url = "https://14.224.192.52:9999/api/v1/products/summary"
response = requests.get(
    url,
    cert=cert,
    verify= CA_CERT_PATH # hoặc verify=False nếu chỉ test
)
print(response.status_code)
product_data = response.json()
print(product_data)

total_products = product_data['total_products']
page_size = 100
numberof_pages = (total_products) // page_size + 1 # page_size  # Làm tròn lên

# POST list /api/v1/products/list
url = "https://14.224.192.52:9999/api/v1/products/list"
merge_df = pd.DataFrame()
# mở conn = sqlite3.connect('data/products_temp.sqlite')
conn = sqlite3.connect('data/products_temp.sqlite')
# Check if table exists
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products';")
table_exists = cursor.fetchone() is not None

if table_exists:
    existing_df = pd.read_sql("SELECT * FROM products", conn)
else:
    existing_df = pd.DataFrame()# Nếu đã có dữ liệu thì lấy số bản ghi hiện tại với số trang hoàn thiện chẵn sỗ, phần lẻ ra bỏ đi
start_page = (len(existing_df) // page_size) + 1 if not existing_df.empty else 1
print(f"Đã có sẵn {len(existing_df)} bản ghi, bắt đầu từ trang {start_page}")
# Loại bỏ những dòng lẻ nếu có
existing_df = existing_df.iloc[:(start_page -1) * page_size]
# Nếu có thể bắt đầu từ trang mà trang đó không phải trang 1 thì gán merge_df = existing_df
if not existing_df.empty:
    merge_df = existing_df

for page in range(start_page, numberof_pages + 1):
    response = requests.post(
        url,
        json={
                "page": page,
                "page_size": page_size,
                "search": ""  # Optional - tìm kiếm theo mã hoặc tên sản phẩm
            },
        cert=cert,
        verify= CA_CERT_PATH # hoặc verify=False nếu chỉ test
    )
    
    print(response.status_code)
    products = response.json()
    print(products)
    split_data = pd.DataFrame(products['items'])
    # xóa cột ten_nhom trong split_data để tránh lỗi khi concat
    split_data = split_data.drop(columns=['ten_nhom'], errors='ignore')
    if page == 1:
        merge_df = split_data
    else:
        merge_df = pd.concat([merge_df, split_data], ignore_index=True)
        print(f"Đã lấy xong trang {page}/{numberof_pages}, độ dài merge_df: {len(merge_df)} bản ghi")
    # if page >= 500:
    #     break  # test 5 page trước
    # ghi merge_df ra sqlite tạm thời
    conn = sqlite3.connect('data/products_temp.sqlite')
    merge_df.to_sql('products', conn, if_exists='replace', index=False) 

# Nếu server dùng self-signed cert, bạn có thể cần ca-cert.pem hoặc tắt verify (không khuyến nghị cho production)
# **Curl Example:**
# ```bash
# curl -X GET "http://localhost:9897/api/v1/categories"
# ```
categories_url = "https://14.224.192.52:9999/api/v1/categories"
response = requests.get(
    categories_url,
    cert=cert,
    verify= CA_CERT_PATH # hoặc verify=False nếu chỉ test
)
print(response.status_code)     
categories = response.json()
print(categories)   
categories_df = pd.DataFrame(categories['items'])
conn = sqlite3.connect('data/products_temp.sqlite')
categories_df.to_sql('categories', conn, if_exists='replace', index=False)

# exit(1)

# call api  GET "http://localhost:9897/api/v1/products/summary"

### 2. POST /api/v1/templates/list
# Lấy danh sách mẫu mã có phân trang 

# **Request Body:**
# ```json
# {
#   "page": 1,
#   "page_size": 20,
#   "search": "24BTV"  // Optional - tìm kiếm theo Ma_NM hoặc Ten_NM
# }
# ```

# **Response:**
# ```json
# {
#   "items": [
#     {
#       "id": 1234,
#       "ma_nm": "24BTV001",
#       "ten_nm": "Bông tai vàng kiểu 1",
#       "nhom_lon": "BT - Bông tai",
#       "nhom_ct": "BTV - Bông tai vàng",
#       "chung_loai": "CL01 - Chung loại 1",
#       "gioi_tinh": "NU - Nữ",
#       "phong_cach": "PC01 - Phong cách hiện đại",
#       "bo_suu_tap": "BST2024 - Bộ sưu tập 2024",
#       "clkl": "18K - Vàng 18K",
#       "ham_luong_kl": "75% - 750/1000",
#       "mau_bm_kl": "VT - Vàng trắng",
#       "ten_da_chu": "RUBY - Ruby đỏ",
#       "so_luong_da_chu": "SL02 - 2 viên",
#       "so_luong_chau": "SL04 - 4 viên",
#       "hinh_dang_da": "TRON - Tròn",
#       "kich_thuoc_da": "3MM - 3mm",
#       "kieu_mai_da": "BRILLIANT - Brilliant cut",
#       "loai_da": "NATURAL - Đá tự nhiên",
#       "chot_bong_tai": "TRAI - Chốt trái",
#       "khoa_bong_tai": "TITAN - Khóa titan",
#       "khoa_day_khuyen": "LOBSTER - Khóa tôm hùm",
#       "khoa_vong_lac": "CAI - Khóa cài",
#       "hinh_dang_vong": "TRON - Hình tròn",
#       "kieu_kim": "STRAIGHT - Kim thẳng",
#       "hoa_tiet": "HOA - Hoa văn hoa lá",
#       "kieu_khac_ma_nv": "LASER - Khắc laser",
#       "hinh_thuc_ma_nv": "QR - Mã QR",
#       "hinh_thuc_td_vl": "CANKIM - Cân kim",
#       "kdkm": "KM01 - Khuyến mãi tháng 11",
#       "ghi_chu": "Mẫu đặc biệt cho dịp lễ",
#       "mo_ta": "Bông tai vàng 18K với ruby đỏ và kim cương",
#       "inactive": false
#     }
#   ],
#   "total": 8542,
#   "page": 1,
#   "page_size": 20,
#   "total_pages": 428
# }
# ```


#  GET /api/v1/categories
# Lấy danh sách tất cả nhóm/danh mục sản phẩm.

# **Response:**
# ```json
# {
#   "items": [
#     {
#       "ma_nhom": "NH001",
#       "ten_nhom": "Nhẫn"
#     },
#     {
#       "ma_nhom": "DC001",
#       "ten_nhom": "Dây chuyền"
#     },
#     {
#       "ma_nhom": "BC001",
#       "ten_nhom": "Bông tai"
#     }
#   ],
#   "total": 45
# }
# ```
template_url = "https://14.224.192.52:9999/api/v1/templates/list"
is_last_page = False
current_page = 1
templates_df = pd.DataFrame()
while not is_last_page:
    response = requests.post(
        template_url,
        json={
                "page": current_page,
                "page_size": 500,
                "search": ""  # Optional
            },
        cert=cert,
        verify= CA_CERT_PATH # hoặc verify=False nếu chỉ test
    )
    print(response.status_code)
    templates = response.json()
    current_page = templates['page']
    total_pages = templates['total_pages']
    is_last_page = current_page >= total_pages
    print(templates)
    
    if current_page == 1:
        templates_df = pd.DataFrame(templates['items'])
    else:
        templates_df = pd.concat([templates_df, pd.DataFrame(templates['items'])], ignore_index=True)
        print(f"Đã lấy xong trang {current_page}/{total_pages}, độ dài templates_df: {len(templates_df)} bản ghi")
    # templates_df.to_excel('data/templates.xlsx', index=False)
    
    conn = sqlite3.connect('data/products_temp.sqlite')
    templates_df.to_sql('templates', conn, if_exists='replace', index=False) 
    current_page += 1



### 1. GET /api/v1/customers/summary
# Lấy thống kê tổng quan về khách hàng.

# **Response:**
# ```json
# {
#   "total_customers": 8523
# }
# ```
sumary_customer_url = "https://14.224.192.52:9999/api/v1/customers/summary"
response = requests.get(
    sumary_customer_url,
    cert=cert,
    verify= CA_CERT_PATH # hoặc verify=False nếu chỉ test
)

url = "https://14.224.192.52:9999/api/v1/customers/list"

total_customers = response.json()['total_customers']
page_size = 500
numberof_pages = (total_customers) // page_size + 1 # page_size  # Làm tròn lên

# POST /api/v1/customers/list
# Lấy danh sách khách hàng có phân trang và tìm kiếm.

# **Request Body:**
# ```json
# {
#   "page": 1,
#   "page_size": 50,
#   "search": "nguyen"  // Optional - tìm kiếm theo mã, tên, SĐT, CCCD
# }
# ```
merge_df = pd.DataFrame()
for page in range(1, numberof_pages + 1):
    response = requests.post(
        url,
        json={
                "page": page,
                "page_size": page_size,
                "search": ""  # Optional - tìm kiếm theo mã, tên, SĐT, CCCD
            },
        cert=cert,
        verify= CA_CERT_PATH # hoặc verify=False nếu chỉ test
    )
    
    print(response.status_code)
    customers = response.json()
    print(customers)
    split_data = pd.DataFrame(customers['items'])
    if page == 1:
        merge_df = split_data
    else:
        merge_df = pd.concat([merge_df, split_data], ignore_index=True)
        print(f"Đã lấy xong trang {page}/{numberof_pages}, độ dài merge_df: {len(merge_df)} bản ghi")
    # if page >= 500:
    #     break  # test 5 page trước
    # ghi merge_df ra sqlite tạm thời
    import sqlite3  
    conn = sqlite3.connect('data/customers_temp.sqlite')
    merge_df.to_sql('customers', conn, if_exists='replace', index=False)

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
