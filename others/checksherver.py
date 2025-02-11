import xmlrpc.client
from datetime import datetime, timezone, timedelta
from minio import Minio
from minio.error import S3Error

# Kết nối tới server Odoo
ODOO_BASE_URL = "https://hrm.mandalahotel.com.vn"
ODOO_DB = "apechrm_product_v3"
ODOO_USERNAME = "admin_ho"
ODOO_PASSWORD = "43a824d3a724da2b59d059d909f13ba0c38fcb82"

# Kết nối tới Minio
client = Minio(
    "42.113.122.201:9000",
    access_key="FLoU4kYrt6EQ8eyWBLjD",
    secret_key="LBa3KybNAxwxHWuFPqKF00ppIi5iOotJXQQzriUa",
    secure=False  # Đặt thành True nếu bạn sử dụng HTTPS
)

# Xác thực người dùng Odoo
common = xmlrpc.client.ServerProxy(f'{ODOO_BASE_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})

# Kết nối tới object trên Odoo
models = xmlrpc.client.ServerProxy(f'{ODOO_BASE_URL}/xmlrpc/2/object')

# Lấy tất cả các dòng từ model "hr.upload.attendance"
attendance_records = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'hr.upload.attendance', 'search_read',
    [[]],  # Điều kiện lọc, ở đây là lấy tất cả
    {'fields': ['id', 'url']}  # Các trường cần lấy
)

# Lưu tất cả các URL từ Odoo vào danh sách
odoo_urls = [record['url'] for record in attendance_records]

# Hàm đệ quy để liệt kê tất cả các tệp trong một bucket và xoá nếu không tồn tại trên Odoo
def list_and_delete_files(bucket_name, prefix=""):
    try:
        objects = client.list_objects(bucket_name, prefix=prefix, recursive=True)
        for obj in objects:
            object_name = obj.object_name[len(prefix):]
            creation_date = obj.last_modified.replace(tzinfo=timezone.utc)
            current_date = datetime.now(timezone.utc)
            # Kiểm tra điều kiện không tồn tại trên Odoo và thời gian tạo cách hiện tại từ 3 ngày trở lên
            if not any(odoo_url.endswith(object_name) for odoo_url in odoo_urls) and (current_date - creation_date).days >= 3:
                print(f"Deleting: {obj.object_name}")
                client.remove_object(bucket_name, obj.object_name)
            else:
                print(f"Keep: {obj.object_name}")
    except S3Error as e:
        print(f"Error occurred: {e}")

# Gọi hàm list_and_delete_files với tên bucket và prefix của bạn
list_and_delete_files("apecerp", "apechrm_product_v3/")

