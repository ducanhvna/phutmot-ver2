import json
import requests


# Config Odoo
url = "http://odoo18:8069/jsonrpc"
db = "goldsun"                          # tên database
username = "admin"                      # user đăng nhập
password = "admin"                      # mật khẩu


# 1. Authenticate
def odoo_authenticate():
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "common",
            "method": "authenticate",
            "args": [db, username, password, {}],
        },
        "id": 1,
    }
    response = requests.post(url, json=payload).json()
    return response.get("result")
uid = 2
try:
    uid = odoo_authenticate()
except Exception as e:
    print("Lỗi khi xác thực với Odoo:", e)
    uid = 2

# 2. Hàm gọi Odoo RPC
def odoo_execute(model, method, args, kwargs=None):
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [db, uid, password, model, method, args],
        },
        "id": 2,
    }
    if kwargs:
        payload["params"]["kwargs"] = kwargs

    response = requests.post(url, json=payload)
    try:
        data = response.json()
    except Exception:
        print("Không parse được JSON, raw response:", response.text)
        raise

    if "error" in data:
        print("Odoo trả về lỗi:", data["error"])
        raise Exception(data["error"])
    if "result" not in data:
        print("Response không có 'result':", data)
        raise Exception("Không có result trong response")

    return data["result"]


def get_or_create_product(product_name, price_unit, company_id):
    # Tìm sản phẩm theo tên
    products = odoo_execute(
        "product.product", "search_read",
        [[["name", "=", product_name]]],
        {"fields": ["id", "name"], "limit": 1}
    )
    if products:
        product_id = products[0]["id"]
        print(f"Đã tìm thấy sản phẩm: {products[0]}")
    else:
        # Nếu chưa có thì tạo mới
        product_data = {
            "name": product_name,
            "list_price": price_unit,
            "company_id": company_id,
            "type": "consu",     # hoặc "service" nếu là dịch vụ
            "sale_ok": True,     # cho phép bán
            "purchase_ok": True, # cho phép mua
            "uom_id": 1,         # đơn vị tính (thường ID=1 là 'Unit(s)')
            "uom_po_id": 1,      # đơn vị mua
            "categ_id": 1,       # phân loại sản phẩm (thường ID=1 là 'All')
        }

        product_id = odoo_execute("product.product", "create", [product_data])
        print(f"Đã tạo sản phẩm mới với ID: {product_id}")
    return product_id
# data =  {"id": 1, "displayName": "An Phương Loan", "phone": "*0819322222", "email": None, "street": "51 nguyễn công trứ , đồng nhân , hai bà trưng , hà nội", "city": None, "stateId": 0, "vat": None, "cccdNumber": None, "cccdVerified": 0, "customerType": "CustomerType.newCustomer", "orderitems": [{"id": 25, "server_id": 0, "order_id": 23, "product_id": 1, "name": "Nhẫn ép vỉ Vàng Rồng Thăng Long, 1 chỉ - 24K (999.9)", "sequence": 1, "quantity": 8, "price_unit": 1000000.0, "discount": 0.0, "tax_ids": 1, "total_price_without_tax": 5400000.0, "total_price_with_tax": 8000000.0, "is_reward": 0, "is_gift": 0, "gift_group_id": 0, "return_reason": None, "original_brand": None, "ham_luong": 0.0, "trong_luong_da": 0.0, "tien_cong_ban": 0.0, "tien_da": 0.0, "is_exchange_return": 0, "exchange_from_order_item_id": None, "service_id": 0, "item_type": "product", "status": "pending", "weight_grams": 0.0, "material": "other", "carat": 0.0, "condition": "new", "product_sku": "TTVRV24KD0-112001", "appraisal_photo_path": None, "created_at": "2025-11-24T08:13:21.809105", "updated_at": "2025-11-24T09:00:29.609628", "deleted_at": None, "deleted_by": 0, "is_synced": 0, "last_sync_at": None}, {"id": 29, "server_id": 0, "order_id": 23, "product_id": 7, "name": "Nhẫn tròn ép vỉ Kim Gia Bảo, loại 1 chỉ - 24K (999.9)", "sequence": 2, "quantity": 7, "price_unit": 1000000.0, "discount": 0.0, "tax_ids": 1, "total_price_without_tax": 6300000.0, "total_price_with_tax": 7000000.0, "is_reward": 0, "is_gift": 0, "gift_group_id": 0, "return_reason": None, "original_brand": None, "ham_luong": 0.0, "trong_luong_da": 0.0, "tien_cong_ban": 0.0, "tien_da": 0.0, "is_exchange_return": 0, "exchange_from_order_item_id": None, "service_id": 0, "item_type": "product", "status": "pending", "weight_grams": 0.0, "material": "other", "carat": 0.0, "condition": "new", "product_sku": "KGB1C", "appraisal_photo_path": None, "created_at": "2025-11-24T08:59:49.860981", "updated_at": "2025-11-24T08:59:49.860981", "deleted_at": None, "deleted_by": 0, "is_synced": 0, "last_sync_at": None}, {id: 30, "server_id": 0, "order_id": 23, "product_id": 4, "name": "Nhẫn ép vỉ Vàng Rổng Thăng Long , 5 chỉ - 24K (999.9)", "sequence": 3, "quantity": 10, "price_unit": 1000000.0, "discount": 0.0, "tax_ids": 1, "total_price_without_tax": 9000000.0, "total_price_with_tax": 10000000.0, "is_reward": 0, "is_gift": 0, "gift_group_id": 0, "return_reason": None, "original_brand": None, "ham_luong": 0.0, "trong_luong_da": 0.0, "tien_cong_ban": 0.0, "tien_da": 0.0, "is_exchange_return": 0, "exchange_from_order_item_id": None, "service_id": 0, "item_type": "product", "status": "pending", "weight_grams": 0.0, "material": "other", "carat": 0.0, "condition": "new", "product_sku": "TTVRV24KD0-112005", "appraisal_photo_path": None, "created_at": "2025-11-24T09:00:23.998840", "updated_at": "2025-11-24T09:00:23.998840", "deleted_at": None, "deleted_by": 0, "is_synced": 0, "last_sync_at": None}, {id: 31, "server_id": 0, "order_id": 23, "product_id": 2, "name": "Nhẫn ép vỉ Vàng Rồng Thăng Long, 2 chỉ - 24K (999.9)", "sequence": 4, "quantity": 9, "price_unit": 1000000.0, "discount": 0.0, "tax_ids": 1, "total_price_without_tax": 8100000.0, "total_price_with_tax": 9000000.0, "is_reward": 0, "is_gift": 0, "gift_group_id": 0, "return_reason": None, "original_brand": None, "ham_luong": 0.0, "trong_luong_da": 0.0, "tien_cong_ban": 0.0, "tien_da": 0.0, "is_exchange_return": 0, "exchange_from_order_item_id": None, "service_id": 0, "item_type": "product", "status": "pending", "weight_grams": 0.0, "material": "other", "carat": 0.0, "condition": "new", "product_sku": "TTVRV24KD0-112002", "appraisal_photo_path": None, "created_at": "2025-11-24T10:56:29.219156", "updated_at": "2025-11-24T10:56:29.219156", "deleted_at": None, "deleted_by": 0, "is_synced": 0, "last_sync_at": None}, {"id": 32, "server_id": 0, "order_id": 23, "product_id": 19, "name": "Nhẫn kim cương thiên nhiên vàng trắng 18K. 1viên 3.6ly, 12 viên 1.4ly, 4viên 1.3ly", "sequence": 5, "quantity": 7, "price_unit": 1000000.0, "discount": 0.0, "tax_ids": 1, "total_price_without_tax": 6300000.0, "total_price_with_tax": 7000000.0, "is_reward": 0, "is_gift": 0, "gift_group_id": 0, "return_reason": None, "original_brand": None, "ham_luong": 0.0, "trong_luong_da": 0.0, "tien_cong_ban": 0.0, "tien_da": 0.0, "is_exchange_return": 0, "exchange_from_order_item_id": None, "service_id": 0, "item_type": "product", "status": "pending", "weight_grams": 0.0, "material": "other", "carat": 0.0, "condition": "new", "product_sku": "TKN2V18KCN-112001", "appraisal_photo_path": None, "created_at": "2025-11-24T10:56:45.445515", "updated_at": "2025-11-24T10:56:45.445515", "deleted_at": None, "deleted_by": 0, "is_synced": 0, "last_sync_at": None}]}

def create_purchase_order_from_json(data):
    # 3. Tạo hoặc lấy khách hàng
    # 4. Kiểm tra khách hàng theo phone
    phone_number = data.get("phone", "").replace("*", "")  # bỏ ký tự *
    partners = odoo_execute(
        "res.partner", "search_read",
        [["|",["phone", "=", phone_number],["mobile", "=", phone_number]]],
        {"fields": ["id", "name", "phone"], "limit": 1}
    )

    if partners:
        partner_id = partners[0]["id"]
        print(f"Khách hàng đã tồn tại: {partners[0]}")
    else:
        partner_data = {
            "name": data.get("displayName"),
            "phone": phone_number,
            "street": data.get("street"),
            "customer_rank": 1,
        }
        partner_id = odoo_execute("res.partner", "create", [partner_data])
        print(f"Đã tạo khách hàng mới với ID: {partner_id}")
    # 5. Tạo đơn hàng
    order_data = {
        "partner_id": partner_id,
    }
    order_id = odoo_execute("purchase.order", "create", [order_data])
    print(f"Đã tạo đơn hàng với ID: {order_id}")
    # 6. Thêm các dòng sản phẩm từ JSON
    for item in data.get("sellorderitems", []):
        product_name = item.get("name")
        price_unit = item.get("price_unit", 0.0)

        product_id = get_or_create_product(product_name, price_unit, 1)

        line_data = {
            "order_id": order_id,
            "product_id": product_id,
            "name": product_name,
            "product_uom_qty": item.get("quantity"),
            "price_unit": price_unit,
        }

        # Nếu có thuế trong JSON, lọc theo company_id
        if item.get("tax_ids"):
            taxes = odoo_execute(
                "account.tax", "search_read",
                [[["id", "=", item["tax_ids"]], ["company_id", "=", 4]]],
                {"fields": ["id"], "limit": 1}
            )
            if taxes:
                line_data["tax_id"] = [(6, 0, [taxes[0]["id"]])]

        odoo_execute("purchase.order.line", "create", [line_data])

    print("Đơn mua và các dòng sản phẩm đã được tạo thành công!")