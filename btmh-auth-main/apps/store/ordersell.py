import os, json
import requests
import datetime
from django.conf import settings
# Config Odoo
url = settings.ODOO_SERVER_URL + "/jsonrpc"
db = settings.ODOO_DB                      # tên database
username = settings.ODOO_USERNAME                      # user đăng nhập
password = settings.ODOO_PASSWORD                      # mật khẩu
from typing import Any, Optional


def normalize_gold_mass(ham_luong_kl: Any) -> float:
    if ham_luong_kl is None:
        return 0.0

    ham_luong_str = str(ham_luong_kl).strip().upper()

    mapping = {
        "99.9": 99.9,
        "999.9": 99.99,
        "KC": 99.99,
        "24K": 99.99,
        "58.5": 58.5,
        "75": 75,
        "41.7": 41.7,
    }

    if ham_luong_str in mapping:
        return mapping[ham_luong_str]

    try:
        return float(ham_luong_str)
    except (ValueError, TypeError):
        return 0.0


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

# 2. Lấy thông tin đơn hàng từ model pos.order
def get_latest_order_id(ma_khachhang, date_str):
    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    tomorrow = (date_obj + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                db,
                uid,
                password,
                "pos.order",
                "search",
                [[
                    ["state", "in", ["draft"]],
                    ["partner_id", "=", ma_khachhang],
                    ["date_order", ">=", date_str],
                    ["date_order", "<", tomorrow]
                ]],
                {"limit": 1, "order": "id desc"},
            ],
        },
        "id": 2,
    }
    response = requests.post(url, json=payload).json()
    order_ids = response.get("result", [])
    if order_ids:
        return order_ids[0]
    return None

def get_pos_order(uid, password, order_id):
    # Lấy thông tin đơn hàng chính
    payload_order = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                db,
                uid,
                password,
                "pos.order",
                "search_read",
                [[["id", "=", order_id]]],
                {
                    "fields": [
                        "id",
                        "name",
                        "partner_id",
                        "amount_total",
                        "partner_phone_masked",
                        "partner_national_id_masked",
                        "date_order",
                        "state",
                        "lines",                  # one2many tới pos.order.line
                        "applied_promotion_ids",  # many2many tới pos.promotion
                    ],
                    "limit": 1,
                },
            ],
        },
        "id": 2,
    }
    response = requests.post(url, json=payload_order).json()
    order = response.get("result")
    if not order:
        return None
    order = order[0]

    # Lấy chi tiết lines
    line_ids = order.get("lines", [])
    lines_detail = []
    if line_ids:
        payload_lines = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    db,
                    uid,
                    password,
                    "pos.order.line",
                    "read",
                    [line_ids],
                    {
                        "fields": [
                            "id",
                            "lot_id",
                            "product_id",
                            "qty",
                            "price_unit",
                            "discount",
                            "price_subtotal",
                        ]
                    },
                ],
            },
            "id": 3,
        }
        resp_lines = requests.post(url, json=payload_lines).json()
        lines_detail = resp_lines.get("result", [])

    # Lấy chi tiết product.template cho từng product_id
    for line in lines_detail:
        product_id = line.get("product_id")
        if product_id:
            # product_id thường là [id, "Tên sản phẩm"]
            pid = product_id[0] if isinstance(product_id, (list, tuple)) else product_id
            payload_product = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute_kw",
                    "args": [
                        db,
                        uid,
                        password,
                        "product.product",
                        "read",
                        [[pid]],
                        {
                            "fields": [
                                "id",
                                "name",
                                "default_code",
                                "list_price",
                                "uom_id",
                                "categ_id",
                            ]
                        },
                    ],
                },
                "id": 4,
            }
            resp_product = requests.post(url, json=payload_product).json()
            product_detail = resp_product.get("result", [])
            line["product_detail"] = product_detail[0] if product_detail else None

    # Lấy chi tiết khuyến mãi
    promo_ids = order.get("applied_promotion_ids", [])
    promotions_detail = []
    if promo_ids:
        payload_promos = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    db,
                    uid,
                    password,
                    "pos.promotion",
                    "read",
                    [promo_ids],
                    {"fields": ["id", "name", "promotion_type", "discount_value"]}
                ],
            },
            "id": 4,
        }
        resp_promos = requests.post(url, json=payload_promos).json()
        promotions_detail = resp_promos.get("result", [])

    # Tính tổng discount từ lines
    total_discount = sum([(line.get("discount", 0) / 100.0) * line.get("price_unit", 0) * line.get("qty", 0)
                          for line in lines_detail])

    # Ghép kết quả
    order_info = {
        "id": order["id"],
        "name": order["name"],
        "partner_id": order["partner_id"],
        "amount_total": order["amount_total"],
        "date_order": order["date_order"],
        "state": order["state"],
        "lines": lines_detail,
        "promotions": promotions_detail,
        "total_discount": total_discount,
    }
    return order_info

def update_pos_order_line(uid, password, line_id, values):
    """
    Cập nhật một pos.order.line với các giá trị mới
    """
    payload_update = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                db,
                uid,
                password,
                "pos.order.line",
                "write",
                [[line_id], values],
            ],
        },
        "id": 5,
    }
    response = requests.post(url, json=payload_update).json()
    return response.get("result")

def unlink_pos_order_lines(uid, password, order_info):
    """
    Xoá toàn bộ pos.order.line của order_info đã lấy trước đó
    """
    line_ids = [line["id"] for line in order_info.get("lines", [])]
    if not line_ids:
        print(f"Order {order_info['id']} không có line nào")
        return True

    payload_unlink = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                db,
                uid,
                password,
                "pos.order.line",
                "unlink",
                [line_ids],
            ],
        },
        "id": 50,
    }
    resp_unlink = requests.post(url, json=payload_unlink).json()
    result = resp_unlink.get("result", False)
    print(f"Unlink lines {line_ids} result: {result}")
    return result


def create_pos_order_line(uid, password, order_id, line_odoo, line_item):
    """
    Tạo mới một pos.order.line cho order_id với dữ liệu từ line_odoo và line_item (API)
    """
    qty = line_odoo.get("qty", 1)
    product_id = line_odoo["product_id"][0] if isinstance(line_odoo["product_id"], (list, tuple)) else line_odoo["product_id"]

    values_to_create = {
        "order_id": order_id,
        "product_id": product_id,
        "qty": qty,
    }

    if "ham_luong_kl" in line_item:
        gold_mass = normalize_gold_mass(line_item.get("ham_luong_kl", ""))
        values_to_create["x_gold_mass"] = gold_mass if gold_mass else 0.0

    if "t_Luong" in line_item:
        values_to_create["gold_weight"] = line_item.get("t_Luong", 0.0)

    if "kl_da" in line_item:
        values_to_create["x_stone_weight"] = line_item.get("kl_da", 0.0)

    if "tong_kl" in line_item:
        values_to_create["x_total_weight"] = line_item.get("tong_kl", 0.0)

    if "tien_cong" in line_item:
        values_to_create["x_labor_cost"] = line_item.get("tien_cong", 0.0)

    if "tien_da" in line_item:
        values_to_create["x_stone_cost"] = line_item.get("tien_da", 0.0)

    if "giaBan" in line_item:
        gia_tien = line_item.get("giaBan", 0.0)
        values_to_create["price_unit"] = 0.0 if gia_tien == 0 or qty == 0 else gia_tien

    if "tien_ck" in line_item:
        values_to_create["x_money_promotion"] = line_item.get("tien_ck", 0.0)

    payload_create = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                db,
                uid,
                password,
                "pos.order.line",
                "create",
                [values_to_create],
            ],
        },
        "id": 51,
    }
    resp_create = requests.post(url, json=payload_create).json()
    print(f"{values_to_create} - resp_create - {resp_create}")
    return resp_create.get("result")


def apply_action(uid, password, order_id, action):
    """
    Thực thi action trên pos.order
    """
    payload_clear = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                db,
                uid,
                password,
                "pos.order",
                action,
                [[order_id]],
            ],
        },
        "id": 60,
    }
    resp_clear = requests.post(url, json=payload_clear).json()
    result = resp_clear.get("result", False)
    print(f"execute {action} for order {order_id} result: {result}")
    return result

def clear_order_promotions(uid, password, order_id):
    """
    Thực thi action_clear_promotions trên pos.order
    """
    return apply_action(uid=uid, password=password, order_id=order_id, action="action_clear_promotions")

def apply_order_promotions(uid, password, order_id):
    """
    Thực thi action_apply_promotions trên pos.order
    """
    return apply_action(uid=uid, password=password, order_id=order_id, action="action_apply_promotions")


def update_product_price(uid, password, product_id, new_price):
    """
    Cập nhật list_price của product.product
    """
    payload_update_price = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                db,
                uid,
                password,
                "product.product",
                "write",
                [[product_id], {"list_price": new_price}],
            ],
        },
        "id": 70,
    }
    resp_update = requests.post(url, json=payload_update_price).json()
    result = resp_update.get("result", False)
    print(f"Update product {product_id} list_price={new_price} result: {result}")
    return result


def sync_pos_order_data(uid, password, order_info, odoo_inventory_code="FS01"):
    price_api_base = os.getenv(f'AUGGES_BASE_URL_{odoo_inventory_code}', 'http://192.168.0.223:8096')
    ma_kho = os.getenv(f'AUGGES_INVENTORY_CODE_{odoo_inventory_code}', 'http://192.168.0.223:8096')

    order_id = order_info["id"]

    # 1. Xoá toàn bộ line cũ
    unlink_pos_order_lines(uid, password, order_info)

    # 2. Clear promotions
    clear_order_promotions(uid, password, order_id)

    # 3. Tạo mới line cho từng sản phẩm
    for line_odoo in order_info.get('lines', []):
        ma_hang = line_odoo['product_detail']['default_code']
        url_api = f"{price_api_base}/api/public/hang_ma_kho/{ma_hang}/{ma_kho}"
        resp = requests.get(url_api, timeout=10)
        payload_api = resp.json()
        line_item = payload_api.get('data', {})

        # --- cập nhật list_price trước khi tạo line ---
        if "giaBan" in line_item:
            gia_tien = line_item.get("giaBan", 0.0)
            product_id = line_odoo["product_id"][0] if isinstance(line_odoo["product_id"], (list, tuple)) else line_odoo["product_id"]
            update_product_price(uid, password, product_id, gia_tien)

        # --- tạo line mới ---
        new_id = create_pos_order_line(uid, password, order_id, line_odoo, line_item)
        print(f"Created new line {new_id} for product {ma_hang}")
    
    apply_order_promotions(uid, password, order_id)


# Ví dụ gọi hàm
# order_info = get_pos_order(uid, password, 43237)
# print(json.dumps(order_info, indent=2, ensure_ascii=False))
