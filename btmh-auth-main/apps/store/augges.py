import requests
import unicodedata

def remove_accents(text):
    """Convert Vietnamese text to non-accented version"""
    if not text:
        return text
    # Normalize to NFD (decomposed form)
    nfd = unicodedata.normalize('NFD', text)
    # Remove combining characters (accents)
    without_accents = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
    # Handle Đ/đ separately
    without_accents = without_accents.replace('Đ', 'D').replace('đ', 'd')
    return without_accents

class AuggesOrderService:
    def __init__(self, order_url):
        headers = {"Content-Type": "application/json; charset=utf-8"}
        self.order_url = order_url
        self.headers = headers

    def create_sell_order_from_odoo(self, odoo_data, data, ma_khachhang):
        """
        odoo_data: dict thông tin đơn hàng từ Odoo (bao gồm lines, promotions, ...)
        data: dict thông tin bổ sung (username_sale, dien_giai, ...)
        ma_khachhang: mã khách hàng trên Augges
        discount_amount: tổng tiền giảm giá (nếu có)
        """
        
        # Chuẩn bị danh sách sản phẩm
        danh_sach = data.get("danh_sach") or []
        items = odoo_data.get("lines", [])

        # Lấy thông tin khuyến mại
        khuyen_mai = odoo_data.get("promotions", [])
        
        # Convert promotion name to non-accented Vietnamese
        promotion_name = "Hop dong tao tu app"
        if khuyen_mai and len(khuyen_mai) > 0:
            original_name = khuyen_mai[0].get("name", "")
            if original_name:
                promotion_name = remove_accents(original_name)

        for item in items:
            product_detail = item.get("product_detail")
            product_sku = product_detail.get("default_code")
            soluong = item.get("qty") or item.get("quantity")
            total_discount = item.get("total_discount", 0)
            money_promotion_total = item.get("money_promotion_total", 0)
            if int(soluong) > 0:
                danh_sach.append({
                    "mahang": product_sku,
                    "soluong": soluong,
                    "so_tien": 0
                    # int(total_discount + money_promotion_total)
                })

        # Thêm giảm giá nếu có
        if odoo_data['total_discount'] > 0:
            danh_sach.append({
                "mahang": "",
                "soluong": 0,
                "so_tien": odoo_data['total_discount']
            })
        else:
            danh_sach.append({
                "mahang": "",
                "soluong": 0,
                "so_tien": 0
            })

        # Nếu không có sản phẩm thì coi như lỗi
        if not danh_sach:
            raise ValueError("Thiếu danh sách sản phẩm")

        # Payload gửi sang Augges
        payload = {
            "ma_khachhang": ma_khachhang,
            "manhanvien": data.get("sale_phone", "0919933911"),
            "dien_giai": promotion_name,
            "danh_sach": danh_sach
        }
        print(payload)
        try:
            response = requests.post(self.order_url, headers=self.headers, json=payload, timeout=30)
            if not response.ok:
                raise RuntimeError(f"Tạo đơn hàng thất bại: {response.status_code} - {response.text}")

            try:
                body = response.json()
                id_don = body.get("data")
                if not id_don:
                    raise RuntimeError("Không nhận được id đơn từ Augges")
                return id_don
            except ValueError:
                raise RuntimeError(f"Phản hồi không phải JSON: {response.text}")

        except requests.RequestException as exc:
            raise RuntimeError(f"Không gọi được dịch vụ đích: {exc}")
