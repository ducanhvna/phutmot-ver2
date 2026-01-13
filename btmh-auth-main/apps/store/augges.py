import requests

class AuggesOrderService:
    def __init__(self, order_url):
        headers = {"Content-Type": "application/json; charset=utf-8"}
        self.order_url = order_url
        self.headers = headers

    def create_sell_order_from_odoo(self, odoo_data, data, ma_khachhang, discount_amount=0):
        """
        odoo_data: dict thông tin đơn hàng từ Odoo (bao gồm lines, promotions, ...)
        data: dict thông tin bổ sung (username_sale, dien_giai, ...)
        ma_khachhang: mã khách hàng trên Augges
        discount_amount: tổng tiền giảm giá (nếu có)
        """

        # Chuẩn bị danh sách sản phẩm
        danh_sach = data.get("danh_sach") or []
        items = odoo_data.get("lines", [])

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
                    "so_tien": int(total_discount + money_promotion_total)
                })

        # Thêm giảm giá nếu có
        if discount_amount > 0:
            danh_sach.append({
                "mahang": "",
                "soluong": 0,
                "so_tien": discount_amount
            })

        # Nếu không có sản phẩm thì coi như lỗi
        if not danh_sach:
            raise ValueError("Thiếu danh sách sản phẩm")

        # Payload gửi sang Augges
        payload = {
            "ma_khachhang": ma_khachhang,
            "manhanvien": data.get("manhanvien", ""),
            "dien_giai": data.get("dien_giai", ""),
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
