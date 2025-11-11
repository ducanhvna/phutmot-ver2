from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .authentication import JWTAuthentication
import datetime

# Giả lập dữ liệu tồn kho
INVENTORY = {
    "SP001": {"name": "Áo thun", "quantity": 25},
    "SP002": {"name": "Quần jean", "quantity": 12},
    "SP003": {"name": "Giày thể thao", "quantity": 8},
}

# Tạo đơn hàng
class OrderView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data
        order_id = f"DH{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        return Response({
            "message": f"Đơn hàng đã tạo bởi {user}",
            "order_id": order_id,
            "items": data.get("items", [])
        })

# Kiểm tra tồn kho
class InventoryCheckView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        product_code = request.query_params.get("code")
        if not product_code:
            return Response({"error": "Thiếu mã sản phẩm"}, status=400)

        product = INVENTORY.get(product_code)
        if not product:
            return Response({"error": "Không tìm thấy sản phẩm"}, status=404)

        return Response({
            "code": product_code,
            "name": product["name"],
            "quantity": product["quantity"]
        })

# In hóa đơn
class PrintInvoiceView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("order_id")
        items = request.data.get("items", [])
        total = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)

        invoice = {
            "order_id": order_id,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": request.user,
            "items": items,
            "total": total,
            "status": "Đã in"
        }

        return Response(invoice)

class AttendanceView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = []  # bỏ check IsAuthenticated nếu không cần

    def post(self, request):
        # Lấy username từ user object "ảo"
        user = getattr(request.user, "username", str(request.user))
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        attendance_info = {
            "user": user,  # <-- trả về chuỗi, không phải object
            "timestamp": now,
            "status": "Đã điểm danh",
            "printserver": {
                "ip": "192.168.1.100",
                "port": 9100,
                "location": "Quầy thu ngân"
            },
            "customer_server": {
                "ip": "192.168.1.100",
                "location": "Cửa hàng chính"
            }
        }

        return Response(attendance_info)

import requests

TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiIs"
BASE_URL = "https://tygia.baotinmanhhai.vn/api"

# Bảng ánh xạ từ mô tả → mã loại vàng chuẩn
reverse_map = {
    "SJC": ["SJC"],
    "VRTL": ["Rồng Thăng Long"],
    "KGB": ["Kim Gia Bảo"],
    "9999": ["999.9", "9999"],
    "999": ["99.9"],
    "BT24K": ["BT 24K"],
    "KHS": ["KHS"],
    "BT-TKC": ["Tiểu Kim Cát", "Trang sức"]
}

class RateView(APIView):
    def get(self, request):
        ma_hang = request.query_params.get("ma_hang")
        if not ma_hang:
            return Response({"error": "Thiếu mã hàng"}, status=400)

        # Mapping mã sản phẩm sang mã loại vàng
        def map_maLoaivang(ma_hang):
            if "SJC" in ma_hang:
                return "SJC"
            elif "VRTL" in ma_hang:
                return "VRTL"
            elif "KGB" in ma_hang:
                return "KGB"
            elif "9999" in ma_hang or "BT24K" in ma_hang:
                return "9999"
            elif "KHS" in ma_hang:
                return "KHS"
            else:
                return "BT-TKC"

        ma_loai_vang = map_maLoaivang(ma_hang)
        url = f"{BASE_URL}/getTyGia/{ma_loai_vang}"
        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json; charset=utf-8"
        }

        try:
            res = requests.get(url, headers=headers)
            data = res.json()

            # Nếu phản hồi thành công và có dữ liệu
            if data.get("status") == 200 and "data" in data:
                for item in data["data"]:
                    original = item.get("loaiVang", "")
                    mapped_code = None
                    for ma, keywords in reverse_map.items():
                        if any(kw.lower() in original.lower() for kw in keywords):
                            mapped_code = ma
                            break
                    item["maLoaivang"] = mapped_code or "UNKNOWN"
                return Response(data)
            else:
                return Response(data, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class AllRateView(APIView):
    def get(self, request):
        url = f"{BASE_URL}/getTyGia"
        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json; charset=utf-8"
        }

        try:
            res = requests.get(url, headers=headers)
            data = res.json()

            if data.get("status") == 200 and "data" in data:
                for item in data["data"]:
                    original = item.get("loaiVang", "")
                    mapped_code = None
                    for ma, keywords in reverse_map.items():
                        if any(kw.lower() in original.lower() for kw in keywords):
                            mapped_code = ma
                            break
                    item["maLoaivang"] = mapped_code or "UNKNOWN"
                return Response(data)
            else:
                return Response(data, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


import pandas as pd

from .data_loader import df_dmH, df_dmQTTG, df_dmVBTG


class PriceCalcView(APIView):
    def get(self, request):
        sku = request.query_params.get("sku")
        if not sku:
            return Response({"error": "Thiếu mã SKU"}, status=400)

        try:
            row = df_dmH[df_dmH['Ma_Hang'] == sku].iloc[0]
            id_qttg = row['ID_QTTG']
            qttg = df_dmQTTG[df_dmQTTG['ID'] == id_qttg].iloc[0]
            ma_qttg = qttg['Ma_QTTG']

            # Gọi API tỷ giá
            url = f"{BASE_URL}/getTyGia"
            headers = {
                "Authorization": f"Bearer {TOKEN}",
                "Content-Type": "application/json; charset=utf-8"
            }
            res = requests.get(url, headers=headers)
            data = res.json()

            # Lấy tỷ giá bán từ mục "Nhẫn ép vỉ Kim Gia Bảo"
            ty_gia_ban = None
            for item in data.get("data", []):
                if "Nhẫn ép vỉ Kim Gia Bảo" in item.get("loaiVang", ""):
                    ty_gia_ban = item.get("giaBanNiemYet")
                    break

            if not ty_gia_ban:
                return Response({"error": "Không tìm thấy tỷ giá Kim Gia Bảo"}, status=500)

            # Tính giá cho các loại sản phẩm đơn giản
            TL_KLoai = row['T_Luong']
            Tien_C_B = row['Gia_Ban5']
            Tien_Da_B = row['Gia_Ban1']

            if ma_qttg in ['GB-24VD', 'GB-BAC', 'GB-KGB', 'GB-SJC', 'GB-VRTL', 'TTXVV24K-GIABAN']:
                gia_ban = TL_KLoai * ty_gia_ban + Tien_C_B + Tien_Da_B
            else:
                gia_ban = None

            return Response({
                "sku": sku,
                "Ma_QTTG": ma_qttg,
                "TyGia_Ban": ty_gia_ban,
                "Gia_Ban": round(gia_ban, -3) if gia_ban else None
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)
