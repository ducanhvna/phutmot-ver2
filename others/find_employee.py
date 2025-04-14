import xmlrpc.client
import pandas as pd
from datetime import datetime, timezone, timedelta
from minio import Minio
from minio.error import S3Error

# Kết nối tới server Odoo
ODOO_BASE_URL = "https://hrm.mandalahotel.com.vn"
ODOO_DB = "apechrm_product_v3"
ODOO_USERNAME = "admin_ho"
ODOO_PASSWORD = "43a824d3a724da2b59d059d909f13ba0c38fcb82"

# Xác thực với Odoo
common = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/common")
uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})

if uid:
    models = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/object")

    # Tìm kiếm nhân viên có tên "Nguyễn Hữu Đức" và mã "APG240408008" với cả trạng thái active/inactive
    employees = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'hr.employee', 'search_read',
        [[['name', '=', 'Nguyễn Hữu Đức'], ['code', '=', 'APG240408008'], ['active', 'in', [True, False]]]],
        {'fields': ['id', 'name', 'active', 'company_id', 'code']}
    )

    # Cập nhật trạng thái và công ty nếu tìm thấy nhân viên
    if employees:
        for emp in employees:
            models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'hr.employee', 'write',
                [[emp['id']], {'active': True, 'company_id': 5}]
            )
            print(f"Đã cập nhật thông tin nhân viên: {emp['name']} (ID: {emp['id']}) thành Active và company_id = 5")
    else:
        print("Không tìm thấy nhân viên nào có tên 'Nguyễn Hữu Đức' và mã 'APG240408008'.")
else:
    print("Lỗi xác thực! Vui lòng kiểm tra thông tin đăng nhập.")
