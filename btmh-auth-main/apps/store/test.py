# run_sync.py
import logging
from django.conf import settings
from apps.store.syncodoo import OdooClient, ApiClient, ProductTemplate, ProductSyncService

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

# 1. Khởi tạo OdooClient bằng cấu hình trong settings
odoo_client = OdooClient(
    base_url=settings.ODOO_SERVER_URL,
    db=settings.ODOO_DB,
    username=settings.ODOO_USERNAME,
    password=settings.ODOO_PASSWORD,
)

# 2. Khởi tạo ApiClient (dùng INTERNAL_API_BASE trong settings)
api_client = ApiClient()

# 3. (Tùy chọn) Khởi tạo helper ProductTemplate nếu cần gọi trực tiếp
product_helper = ProductTemplate(odoo=odoo_client)

# 4. Khởi tạo service đồng bộ
sync_service = ProductSyncService(odoo_client, api_client)

# 5. Ví dụ: đồng bộ 1 mã (có serial)
code = "QTTVV49KD0-504001-132"
warehouse_code = "FS01"
result = sync_service.sync_product_and_serial(code, warehouse_code)
print("Sync result: %s", result)

# 6. Ví dụ: đồng bộ 1 mã (không có serial)
code2 = "QTTVV49KD0-504001-132"
result2 = sync_service.sync_product_and_serial(code2, warehouse_code)
print("Sync result: %s", result2)

# 7. Ví dụ: đồng bộ nhiều mã theo danh sách
codes = ["QTTVV49KD0-504001-132", "BABTB95CZH-511006-003","QTTVV49KD0-504001-058","BTBTV10KDH-511002-005", "QTTVV49KD0-504001-063"]
for c in codes:
    try:
        res = sync_service.sync_product_and_serial(c, warehouse_code)
        print("Synced %s -> %s", c, res)
    except Exception as e:
        print("Failed to sync %s: %s", c, e)
