from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from .authentication import JWTAuthentication
import pandas as pd
from .data_loader import df_dmH, df_dmQTTG, df_dmVBTG, cert, CA_CERT_PATH
import math
import numpy as np
import datetime
from .ordersell import create_order_from_json
from .orderpurchase import create_purchase_order_from_json
from .orderdeposit import create_deposit_order_from_json
from .orderservice import create_service_order_from_json
from .orderreplace import create_replace_order_from_json
from .tasks import poll_payment_and_confirm
import requests
import json
from base64 import b64encode
from urllib.parse import urlencode
import psycopg2
from apps.home.utils import ApiResponse   # <-- class chuẩn hóa response
from rest_framework.pagination import PageNumberPagination

try:
    import pyodbc
except ImportError:  # pragma: no cover - optional dependency
    pyodbc = None

INTERNAL_API_BASE = getattr(settings, "INTERNAL_API_BASE", "http://118.70.146.150:8869")

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
        """
        API kiểm tra tồn kho sản phẩm.

        📌 Endpoint:
        GET /api/inventory/check/?code=SP001

        📤 Response ví dụ (HTTP 200):
        {
            "success": true,
            "message": "Thông tin tồn kho",
            "data": {
                "code": "SP001",
                "name": "Áo thun",
                "quantity": 25
            }
        }

        📤 Response ví dụ (HTTP 404):
        {
            "success": false,
            "message": "Không tìm thấy sản phẩm",
            "data": []
        }
        """
        product_code = request.query_params.get("code")
        if not product_code:
            return ApiResponse.error(message="Thiếu mã sản phẩm", status=400)

        product = INVENTORY.get(product_code)
        if not product:
            return ApiResponse.error(message="Không tìm thấy sản phẩm", status=404)

        return ApiResponse.success(
            message="Thông tin tồn kho",
            data={
                "code": product_code,
                "name": product["name"],
                "quantity": product["quantity"]
            }
        )


class PrintInvoiceView(APIView):
    """
    API in hóa đơn.

    📌 Endpoint:
    POST /api/invoice/print/

    📥 Request body ví dụ:
    {
        "order_id": "DH20251208195900",
        "items": [
            {"name": "Áo thun", "price": 120000, "quantity": 2},
            {"name": "Quần jean", "price": 350000, "quantity": 1}
        ]
    }

    📤 Response ví dụ (HTTP 200):
    {
        "success": true,
        "message": "In hóa đơn thành công",
        "data": {
            "order_id": "DH20251208195900",
            "date": "2025-12-08 20:05:00",
            "user": "admin",
            "items": [
                {"name": "Áo thun", "price": 120000, "quantity": 2},
                {"name": "Quần jean", "price": 350000, "quantity": 1}
            ],
            "total": 590000,
            "status": "Đã in"
        }
    }

    📤 Response ví dụ (HTTP 400 - thiếu order_id):
    {
        "success": false,
        "message": "Thiếu mã đơn hàng",
        "data": []
    }
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("order_id")
        if not order_id:
            return ApiResponse.error(message="Thiếu mã đơn hàng", status=400)

        items = request.data.get("items", [])
        total = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)

        invoice = {
            "order_id": order_id,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": getattr(request.user, "username", str(request.user)),
            "items": items,
            "total": total,
            "status": "Đã in"
        }

        return ApiResponse.success(
            message="In hóa đơn thành công",
            data=invoice
        )


class AttendanceView(APIView):
    """
    API điểm danh nhân viên.

    📌 Endpoint:
    POST /api/attendance/

    📥 Request body ví dụ:
    {
        "username": "admin"
    }

    📤 Response ví dụ (HTTP 200):
    {
        "success": true,
        "message": "Điểm danh thành công",
        "data": {
            "user": "admin",
            "timestamp": "2025-12-08 20:10:00",
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
    }

    📤 Response ví dụ (HTTP 400 - thiếu username):
    {
        "success": false,
        "message": "Thiếu thông tin username",
        "data": []
    }
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = []  # bỏ check IsAuthenticated nếu không cần


    def post(self, request):
        user = getattr(request.user, "username", str(request.user))
        if not user:
            return ApiResponse.error(message="Thiếu thông tin username", status=400)

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        attendance_info = {
            "user": user,
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

        return ApiResponse.success(
            message="Điểm danh thành công",
            data=attendance_info
        )


TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiIs"
BASE_URL = "https://tygia.baotinmanhhai.vn/api"

# Bảng ánh xạ từ mô tả → mã loại vàng chuẩn
reverse_map = {
    "SJC": ["SJC"],
    "VRTL": ["Rồng Thăng Long"],
    "KGB": ["ép vỉ Kim Gia Bảo"],
    "9999": ["999.9", "9999"],
    "999": ["99.9"],
    "BT24K": ["BT 24K"],
    "KHS": ["Đồng vàng Kim Gia Bảo"],
    "BT-TKC": ["Tiểu Kim Cát", "Trang sức"]
}

class RateView(APIView):
    def get(self, request):
        url_tygia_k = "https://14.224.192.52:9999/api/v1/tigia"
        response = requests.get(
            url_tygia_k, 
            cert=cert,
            verify= CA_CERT_PATH) # hoặc verify=False nếu chỉ test
        tygia_k_data = response.json().get('items', [])
        rate_9999 = next((item for item in tygia_k_data if 'Vàng nữ trang 999.9' == item['Ten_VBTG']), None)
        rate_999 = next((item for item in tygia_k_data if 'Vàng nữ trang 99.9' == item['Ten_VBTG']), None) 

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
                    if mapped_code == "9999":
                        item['ty_gia_K'] = rate_9999.get('TyGia_MuaK') if rate_9999 else None
                    elif mapped_code == "999":
                        item['ty_gia_K'] = rate_999.get('TyGia_MuaK') if rate_999 else None
                    else:
                        item['ty_gia_K'] = None
                return Response(data)
            else:
                return Response(data, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class AllRateView(APIView):
    def get(self, request):
        url_tygia_k = "https://14.224.192.52:9999/api/v1/tigia"
        response = requests.get(
            url_tygia_k, 
            cert=cert,
            verify= CA_CERT_PATH) # hoặc verify=False nếu chỉ test
        tygia_k_data = response.json().get('items', [])
        #  {'Ten_VBTG': 'Vàng nữ trang 999.9',
        #     'TyGia_MuaK': 14000000.0,
        #     'TyGia_Mua': 14610000.0,
        #     'TyGia_Ban': 14940000.0},
        #     {'Ten_VBTG': 'Vàng nữ trang 99.9',
        #     'TyGia_MuaK': 13950000.0,
        #     'TyGia_Mua': 14600000.0,
        #     'TyGia_Ban': 14930000.0}],
        # lấy tỷ giá từ mảng với 2 tỷ gia 999.9 và 99.9 như trên
        rate_9999 = next((item for item in tygia_k_data if 'Vàng nữ trang 999.9' == item['Ten_VBTG']), None)
        rate_999 = next((item for item in tygia_k_data if 'Vàng nữ trang 99.9' == item['Ten_VBTG']), None) 

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
                    if mapped_code == "9999":
                        item['ty_gia_K'] = rate_9999.get('TyGia_MuaK') if rate_9999 else None
                    elif mapped_code == "999":
                        item['ty_gia_K'] = rate_999.get('TyGia_MuaK') if rate_999 else None
                    else:
                        item['ty_gia_K'] = None
                return Response(data)
            else:
                return Response(data, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


# Hàm xử lý giá trị float an toàn cho JSON
def sanitize_json_floats(data):
    if isinstance(data, dict):
        return {k: sanitize_json_floats(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_json_floats(v) for v in data]
    elif isinstance(data, float):
        if math.isnan(data) or math.isinf(data):
            return None
        return data
    elif isinstance(data, np.floating):
        if np.isnan(data) or np.isinf(data):
            return None
        return float(data)
    else:
        return data

url = "https://14.224.192.52:9999/api/v1/calculate-price"

# Nếu server dùng self-signed cert, bạn có thể cần ca-cert.pem hoặc tắt verify (không khuyến nghị cho production)
# response = requests.post(
#     url,
#     json={"ma_hang": "KGB1C10022001"},
#     cert=cert,
#     verify= CA_CERT_PATH # hoặc verify=False nếu chỉ test
# )

def tinh_gia_ban(row):
    sku = f"{row['Ma_Hang']}"
    response = requests.post(
        url,
        json={"ma_hang": sku},
        cert=cert,
        verify= CA_CERT_PATH # hoặc verify=False nếu chỉ test
    )
    tygia = response.json()
    # Lấy dữ liệu liên quan từ các bảng
    # qttg_row = df_dmQTTG[df_dmQTTG['ID'] == row['ID_QTTG']].squeeze()
    # vbtg_row = df_dmVBTG[df_dmVBTG['ID'] == row['ID_VBTG']].squeeze()

    # Các biến cần thiết
    TL_KLoai = row['T_Luong']
    TL_Da_C = row['The_Tich']
    T_LuongTT = row['T_LuongTT']
    Tien_Da_B = row['Gia_Ban1']
    Tien_Da_BN = row['Gia_Ban2']
    Tien_C_B = row['Gia_Ban5']
    Tien_C_BN = row['Gia_Ban6']
    Tien_Da_M = row['Gia_Ban3']
    Tien_Da_MN = row['Gia_Ban4']
    Tien_C_M = row['Gia_Ban7']
    Tien_C_MN = row['Gia_Ban8']
    Gia_B_TG = row['Gia_Ban9']
    Gia_B_TGN = row['Gia_Ban10']
    Gia_M_TG = row['Gia_Ban11']
    Gia_M_TGN = row['Gia_Ban12']
    TyGia_Ban = tygia['ty_gia_vang_ban_niem_yet']
    TG_Mua_NY = tygia['ty_gia_vang_mua_niem_yet']
    Tygia_Mua = tygia['ty_gia_vang_mua_niem_yet']
    TyGia_TT = tygia['ty_gia_tien_te_ban_niem_yet']
    TyGiaV_TG = row['Sl_Min']
    TyGia_MuaN = row['Luu_Kho']
    Hao_G_Cong = row['Tyle_GBL']
    # Ma_QTTG = qttg_row['Ma_QTTG']
    Ma_QTTG = tygia['ma_quy_tac_tinh_gia']
    # He_So1 = qttg_row['He_So1']
    He_So1 = tygia['he_so_1']
    # He_So2 = qttg_row['He_So2']
    He_So2 = tygia['he_so_2']
    # He_So3 = qttg_row['He_So3']
    He_So3 = tygia['he_so_3']
    # He_So4 = qttg_row['He_So4']
    He_So4 = tygia['he_so_4']
    # He_So5 = qttg_row['He_So5']
    He_So5 = tygia['he_so_5']
    # He_So6 = qttg_row['He_So6']
    He_So6 = tygia['he_so_6']

    Tong_TL = TL_KLoai + TL_Da_C + T_LuongTT

    # Logic tính giá theo Ma_QTTG
    if Ma_QTTG in ['GB-10K-ORD', 'GB-14K-ORD', 'GB-18K-ORD']:
        result = He_So1 * He_So2 * TyGia_Ban * TL_KLoai + Tien_C_B + Tien_Da_B + Tien_Da_BN * TyGia_TT
    elif Ma_QTTG == 'GB-24VD':
        result = TL_KLoai * TyGia_Ban + Tien_C_B + Tien_Da_B + Tien_Da_BN * TyGia_TT
    elif Ma_QTTG == 'GB-BA-TG':
        result = Gia_B_TG + Tien_C_B + Tien_Da_B + Tien_Da_BN * TyGia_TT
    elif Ma_QTTG == 'GB-BAC':
        result = TL_KLoai * TyGia_Ban + Tien_C_B + Tien_Da_B
    elif Ma_QTTG.startswith('GB-CN-CC') or Ma_QTTG == 'GB-CN-PT':
        result = Tong_TL * (TyGia_Ban + He_So1 * He_So2) + Tien_Da_B + Tien_Da_BN * TyGia_TT
    elif Ma_QTTG == 'GB-CN-TG':
        result = Gia_B_TG + Gia_B_TGN * TyGia_TT
    elif Ma_QTTG == 'GB-KGB':
        result = TL_KLoai * TyGia_Ban
    elif Ma_QTTG.startswith('GB-NC-1'):
        result = Tong_TL * (TyGiaV_TG + He_So1)
    elif Ma_QTTG.startswith('GB-NC-CC') or Ma_QTTG == 'GB-NC-PT':
        result = Tong_TL * (TyGia_Ban + He_So1 * He_So2) + Tien_Da_B + Tien_Da_BN * TyGia_TT
    elif Ma_QTTG.startswith('GB-NCKC-1'):
        result = He_So1 * (TL_KLoai * TyGiaV_TG + Tien_C_M + Tien_C_MN * TyGia_MuaN + Tien_Da_M + Tien_Da_MN * TyGia_MuaN)
    elif Ma_QTTG.startswith('GB-NH-1'):
        result = Tong_TL * (TyGiaV_TG + He_So1)
    elif Ma_QTTG.startswith('GB-PH-1'):
        result = TyGiaV_TG * Tong_TL * He_So1
    elif Ma_QTTG == 'GB-PH-TG':
        result = Gia_B_TG + Gia_B_TGN * TyGia_TT
    elif Ma_QTTG == 'GB-PT':
        result = Gia_B_TG + Gia_B_TGN * TyGia_TT
    elif Ma_QTTG.startswith('GB-PY-1'):
        result = Tong_TL * (TyGiaV_TG + He_So1)
    elif Ma_QTTG.startswith('GB-PY-CC') or Ma_QTTG == 'GB-PY-PT':
        result = Tong_TL * (TyGia_Ban + He_So1 * He_So2)
    elif Ma_QTTG == 'GB-SJC':
        result = TL_KLoai * TyGia_Ban
    elif Ma_QTTG == 'GB-TK-TG':
        result = Gia_B_TG + Gia_B_TGN * TyGia_TT + Tien_Da_B + Tien_Da_BN * TyGia_TT
    elif Ma_QTTG == 'GB-VRTL':
        result = TL_KLoai * TyGia_Ban
    elif Ma_QTTG.startswith('GB-VT-1'):
        result = He_So1 * (TL_KLoai * He_So2 * TyGiaV_TG + Tien_Da_M + (Tien_C_M + TL_KLoai * Hao_G_Cong * Tygia_Mua / He_So2)) + He_So4
    elif Ma_QTTG == 'GB-VT-TG':
        result = Gia_B_TG + Gia_B_TGN * TyGia_TT
    elif Ma_QTTG == 'TRONGOI-GB':
        result = Gia_B_TG + Gia_B_TGN * TyGia_TT
    elif Ma_QTTG == 'TTXVV24K-GIABAN':
        result = TL_KLoai * TyGia_Ban
    else:
        result = 0

    return round(result, -3), tygia

class PriceCalcView(APIView):
    def get(self, request):
        sku = request.query_params.get("sku")
        code = request.query_params.get("code")
        

        if not sku:
            return Response({"status": 400, "msg": "Thiếu mã sản phẩm"}, status=400)
        

        try:
            # Tìm sản phẩm theo SKU
            row = df_dmH[df_dmH["Ma_Hang"] == sku]
            if row.empty:
                # Tìm kiếm những row có Ma_Hang bắt đầu băng sku
                row = df_dmH[df_dmH["Ma_Hang"].notna() & df_dmH["Ma_Hang"].astype(str).str.startswith(sku)]

                if row.empty:
                    return Response({"status": 404, "msg": "Không tìm thấy sản phẩm"}, status=404)
            for _index, r in row.iterrows():
                try:
                
                    gia_ban_v2, realtime_price = tinh_gia_ban(r)
                    row = r
                    break
                except Exception as e:
                    continue
            # Gọi API tỷ giá
            url = f"{BASE_URL}/getTyGia"
            headers = {
                "Authorization": f"Bearer {TOKEN}",
                "Content-Type": "application/json; charset=utf-8"
            }
            res = requests.get(url, headers=headers)
            data = res.json()

            # Lấy tỷ giá bán từ "Nhẫn ép vỉ Kim Gia Bảo"
            ty_gia_ban = None
            rate_data = data.get("data", [])
            for item in rate_data:
                if "Nhẫn ép vỉ Kim Gia Bảo" in item.get("loaiVang", ""):
                    ty_gia_ban = item.get("giaBanNiemYet")
                    break

            if not ty_gia_ban:
                return Response({"status": 500, "msg": "Không tìm thấy tỷ giá Kim Gia Bảo"}, status=500)

            # Tính giá bán = trọng lượng × tỷ giá
            trong_luong = row.get("T_Luong", 0.0)
            if pd.isna(trong_luong):
                trong_luong = 0.0

            gia_ban = round(trong_luong * ty_gia_ban, -3)
            gia_mua = round(trong_luong * ty_gia_ban * 0.98, -3)

            # Trả về dữ liệu theo cấu trúc yêu cầu
            response_data = {
                "id": int(row["ID"]),
                "maSanPham": row["Ma_Hang"],
                "tenSanPham": row["Ten_Hang"],
                "maVach": int(row["Ma_Vach"]),
                "donViTinh": "Chiếc",
                "tenHang": row.get("Ten_Hang1", "") or "",
                "maNhom": row.get("Ma_Tong", "") or "",
                "nguonNhap": "Phòng Cung ứng",
                "ngayNhap": str(row["Ngay_Nhap"]) if not pd.isna(row["Ngay_Nhap"]) else None,
                "quyCach": row.get("Qui_Cach", "") or "",
                "inTrenHoaDon": row["Ten_Hang"],
                "trongLuongKimLoai": trong_luong,
                "trongLuongDaChinh": 0.0,
                "trongLuongDaPhu": 0.0,
                "trongLuongTem": 0.0,
                "tienDaBan": 0.0,
                "tienDaBanUsd": 0.0,
                "tienCongBan": 0.0,
                "tienCongBanUsd": 0.0,
                "giaBan": gia_ban,
                "nhaCungCap": "CTY",
                "soLo": "",
                "baoHanhHanSuDung": None,
                "tieuChuan": "",
                "xuatXu": "",
                "soSeri": "",
                "kich_co": "",
                "ma_tong": row.get("Ma_Tong", "") or "",
                "encodedString": None,
                "giamua": gia_mua,
                "ton_kho": 0,
                "hamLuongKL": "24K",
                "t_Luong": trong_luong,
                "mo_Ta1": row.get("Mo_Ta", "") or "",
                "trongluong": trong_luong,
                "code": code if code else "dummy_code"
            }
            # realtime_price['code'] = code if code else "dummy_code"
            # Làm sạch dữ liệu trước khi trả về
            # cleaned_data = sanitize_json_floats(response_data)

            return Response({
                "status": 200,
                "msg": "Successfully",
                "data": realtime_price,
                # "data": cleaned_data,
                "rate": rate_data,
                # "realtime_price": realtime_price,
                "gia_ban_thamchieu": gia_ban_v2
            })

        except Exception as e:
            return Response({"status": 500, "msg": str(e)}, status=500)

class GenQRView(APIView):
    def post(self, request):
        # account_type = request.data.get("account_type")
        # account_no = request.data.get("account_no")
        amount = request.data.get("amount")
        add_info = request.data.get("add_info")
        transfer_tracking_id = request.data.get("transfer_tracking_id", None)
        
        response = requests.post(
            "https://14.224.192.52:9999/api/v1/generate-qr",
            json={
                "account_type": "1",
                "account_no": "00045627001",
                "amount": amount,
                "add_info": add_info,
                "transfer_tracking_id": transfer_tracking_id if transfer_tracking_id else "NEWTRACKID001"
            },
            cert=cert,
            verify= CA_CERT_PATH # hoặc verify=False nếu chỉ test
        )
        qr = response.json()
        return Response({
            "status": 200,
            "msg": "Successfully",
            "data": qr['qr_data'],
            "account_type": "1",
            "account_no": "00045627001",
            "amount": amount,
            "add_info": add_info,
            "transfer_tracking_id": transfer_tracking_id if transfer_tracking_id else "NEWTRACKID001"
        })
    
class PaymentView(APIView):
    """
    xử lý thanh toán đơn hàng cho khách và trả lại tracking code
    transfer_tracking_id được tạo bởi service nếu client không gửi lên 
    (trong trường hợp client muốn tự tra cứu tracking_id thì gửi lên transfer_tracking_id)
    Response mẫu:

    {
        status_code: ""..."",  
        error_code:""..."",
        error_message: ""..."",
        transaction_id: ""BTMHVPBYYYYMMDDxxxxx....""
        transfer_data: {
            source_account: ""..."",
            amount: ""...."",
            destination_citad_code: ""..."",
            destination_napas_code: ""..."",
            destination_account: ""..."",
            destination_name: ""..."",
            model: ""...."",  
            record_id: ""..."",
            add_info: ""..."",
            status_transfer: ""SUCCESS"",
            transfer_tracking_id: ""BTMHABCD...""
            response_datetime: format DD/MM/YYYY HH24:MI:SS, ví dụ 28/08/2024 10:44:00 timezone ở việt nam
            signature: <Odoo + transaction_id + source_account + amount + destination_citad_code + destination_napas_code + destination_account + destination_name + model + record_id + status_transfer + response_time> (RSAwithSHA256)
            }
        }
    
    """
    def post(self, request):
        transaction_id = request.data.get("transaction_id")
        source_account = request.data.get("source_account")
        amount = request.data.get("amount")
        destination_citad_code = request.data.get("destination_citad_code")
        destination_napas_code = request.data.get("destination_napas_code")
        destination_account = request.data.get("destination_account")
        destination_name = request.data.get("destination_name")
        model = request.data.get("model")
        record_id = request.data.get("record_id")
        add_info = request.data.get("add_info")
        transfer_tracking_id = request.data.get("transfer_tracking_id", "")

        payload = {
            "transaction_id": transaction_id,
            "source_account": source_account,
            "amount": amount,
            "destination_citad_code": destination_citad_code,
            "destination_napas_code": destination_napas_code,
            "destination_account": destination_account,
            "destination_name": destination_name,
            "model": model,
            "record_id": record_id,
            "add_info": add_info
        }

        if transfer_tracking_id:
            payload["transfer_tracking_id"] = transfer_tracking_id

        # Kiểm tra trường hợp tạo mới hay tra cứu để trả về response tương ứng
        # dumy các thông tin ngoài transfer_tracking_id

        return Response({
            "status_code": "200",   
            "error_code": "",
            "error_message": "",    
            "transaction_id": transaction_id,
            "transfer_data": {
                "source_account": source_account,
                "amount": amount,
                "destination_citad_code": destination_citad_code,
                "destination_napas_code": destination_napas_code,
                "destination_account": destination_account,
                "destination_name": destination_name,
                "model": model,
                "record_id": record_id,
                "add_info": add_info,
                "status_transfer": "SUCCESS",
                "transfer_tracking_id": transfer_tracking_id if transfer_tracking_id else "BTMHVPB202406270001",
                "response_datetime": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "signature": "DUMMY_SIGNATURE"
            }
        })
    
    
class PaymentQRProxyView(APIView):
    """
    API tạo QR thanh toán qua dịch vụ Sepay.

    📌 Endpoint:
    POST /api/payment/qr/

    📥 Request body ví dụ:
    {
        "id_don": "DH20251208195900",
        "taikhoanthuhuong": "123456789",
        "noidungchuyentien": "Thanh toán đơn hàng DH20251208195900",
        "sotien": 500000
    }

    📤 Response ví dụ (HTTP 200):
    {
        "success": true,
        "message": "Tạo QR thành công",
        "data": {
            "qr_url": "https://qr.sepay.vn/img?acc=123456789&bank=TPB&amount=500000&des=Thanh toán đơn hàng DH20251208195900&download=0",
            "qr_image_base64": "<base64 của ảnh QR>",
            "params": {
                "acc": "123456789",
                "bank": "TPB",
                "amount": 500000,
                "des": "Thanh toán đơn hàng DH20251208195900",
                "download": 0
            }
        }
    }

    📤 Response ví dụ (HTTP 400 - thiếu trường):
    {
        "success": false,
        "message": "Thiếu trường bắt buộc",
        "data": ["id_don", "sotien"]
    }

    📤 Response ví dụ (HTTP 502 - lỗi kết nối dịch vụ QR):
    {
        "success": false,
        "message": "Không kết nối được dịch vụ QR",
        "data": {
            "error": "Timeout",
            "params": { ... }
        }
    }
    """
    sepay_base = "https://qr.sepay.vn/img"

    def post(self, request):
        data = request.data
        id_don = data.get("id_don")
        taikhoan = data.get("taikhoanthuhuong")
        noidung = data.get("noidungchuyentien")
        sotien = data.get("sotien")
        bank_code = "TPB"

        missing = []
        if not id_don:
            missing.append("id_don")
        if not taikhoan:
            missing.append("taikhoanthuhuong")
        if not noidung:
            missing.append("noidungchuyentien")
        if sotien in (None, ""):
            missing.append("sotien")
        if missing:
            return ApiResponse.error(
                message="Thiếu trường bắt buộc",
                data=missing,
                status=400
            )

        params = {
            "acc": taikhoan,
            "bank": bank_code,
            "amount": sotien,
            "des": noidung,
            "download": 0,
        }

        query = urlencode(params, safe=":/")
        qr_url = f"{self.sepay_base}?{query}"

        try:
            response = requests.get(qr_url, timeout=30)
            response.raise_for_status()
            img_b64 = b64encode(response.content).decode("ascii")

            return ApiResponse.success(
                message="Tạo QR thành công",
                data={
                    "qr_url": qr_url,
                    "qr_image_base64": img_b64,
                    "params": params,
                }
            )
        except requests.RequestException as exc:
            return ApiResponse.error(
                message="Không kết nối được dịch vụ QR",
                data={"error": str(exc), "params": params},
                status=502
            )


class OrderSellView(APIView):
    """
    API tạo đơn hàng bán.

    📌 Endpoint:
    POST /api/order/sell/

    📥 Request body ví dụ:
    {
        "customer_id": 1,
        "items": [
            {"product_id": "SP001", "quantity": 2},
            {"product_id": "SP002", "quantity": 1}
        ]
    }

    📤 Response ví dụ (HTTP 200):
    {
        "success": true,
        "message": "Đơn hàng đã được tạo thành công!",
        "data": []
    }

    📤 Response ví dụ (HTTP 500 - lỗi hệ thống):
    {
        "success": false,
        "message": "Lỗi: Không thể tạo đơn hàng",
        "data": []
    }
    """
    def post(self, request):
        order_data = request.data
        try:
            create_order_from_json(order_data)
            return ApiResponse.success(
                message="Đơn hàng đã được tạo thành công!",
                data=[]
            )
        except Exception as e:
            return ApiResponse.error(
                message=f"Lỗi: {str(e)}",
                status=500
            )

class OrderShellView(APIView):
    """
    API tạo đơn hàng bán (đẩy sang hệ thống nội bộ).

    📌 Endpoint:
    POST /api/order/shell/

    📥 Request body ví dụ:
    {
        "ma_khachhang": "KH001",
        "username_sale": "admin",
        "dien_giai": "Bán hàng tại quầy",
        "sellorderitems": [
            {"product_id": "SP001", "quantity": 2},
            {"product_id": "SP002", "quantity": 1}
        ],
        "discount_amount": 50000
    }

    📤 Response ví dụ (HTTP 200):
    {
        "success": true,
        "message": "Tạo đơn hàng thành công",
        "data": {
            "id_don": "DH20251208195900",
            "so_tien": 450000,
            "downstream": { ... },   # dữ liệu trả về từ hệ thống nội bộ
            "payload": { ... }       # payload gửi đi
        }
    }

    📤 Response ví dụ (HTTP 400 - thiếu mã khách hàng):
    {
        "success": false,
        "message": "Thiếu thông tin mã khách hàng",
        "data": {
            "payload": { ... }
        }
    }

    📤 Response ví dụ (HTTP 400 - thiếu danh sách sản phẩm):
    {
        "success": false,
        "message": "Thiếu danh sách sản phẩm",
        "data": {
            "payload": { ... },
            "sellorderitems": []
        }
    }

    📤 Response ví dụ (HTTP 502 - lỗi kết nối dịch vụ nội bộ):
    {
        "success": false,
        "message": "Không gọi được dịch vụ đích",
        "data": {
            "error": "Timeout",
            "payload": { ... }
        }
    }
    """
    order_url = f"{INTERNAL_API_BASE}/api/public/updatedatehang"
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }

    def post(self, request):
        payload_source = request.data
        if isinstance(payload_source, dict) and isinstance(payload_source.get("data"), dict):
            data = payload_source.get("data")
        else:
            data = payload_source

        ma_khachhang = data.get("ma_khachhang") or data.get("phone", "").replace("*", "")
        discount_amount = data.get("discount_amount", 0)

        if not ma_khachhang:
            return ApiResponse.error(
                message="Thiếu thông tin mã khách hàng",
                data={"payload": data},
                status=400
            )

        danh_sach = data.get("danh_sach") or []
        items = data.get("sellorderitems", [])
        for item in items:
            product_id = item.get("product_id")
            soluong = item.get("quantity")
            if int(soluong) > 0:
                danh_sach.append({
                    "mahang": str(product_id),
                    "soluong": item.get("quantity"),
                    "so_tien": 0
                })
        if discount_amount > 0:
            danh_sach.append({
                "mahang": "",
                "soluong": 0,
                "so_tien": discount_amount
            })
        if not danh_sach:
            return ApiResponse.error(
                message="Thiếu danh sách sản phẩm",
                data={
                    "payload": data,
                    "sellorderitems": data.get("sellorderitems", [])
                },
                status=400
            )

        payload = {
            "ma_khachhang": ma_khachhang,
            "manhanvien": data.get("username_sale", ""),
            "dien_giai": data.get("dien_giai", ""),
            "danh_sach": danh_sach
        }

        try:
            response = requests.post(self.order_url, headers=self.headers, json=payload, timeout=30)
            try:
                body = response.json()
                id_don = body.get('data', {})
                resp = requests.get(f"{INTERNAL_API_BASE}/api/public/chi_tiet_don_hang/{id_don}", timeout=30)
                so_tien = resp.json()["data"]["tong_tien"] - resp.json()["data"].get("tien_ck", 0)
            except ValueError:
                body = {"raw": response.text}
                id_don = None
                so_tien = None

            return ApiResponse.success(
                message="Tạo đơn hàng thành công" if response.ok else "Tạo đơn hàng thất bại",
                data={
                    "id_don": id_don,
                    "so_tien": so_tien,
                    "downstream": body,
                    "payload": payload
                },
                status=response.status_code
            )
        except requests.RequestException as exc:
            return ApiResponse.error(
                message="Không gọi được dịch vụ đích",
                data={"error": str(exc), "payload": payload},
                status=502
            )

class OrderDeTailView(APIView):
    """
    API lấy chi tiết đơn hàng.

    📌 Endpoint:
    POST /api/order/detail/

    📥 Request body ví dụ:
    {
        "ma_don_hang": "DH20251208195900"
    }

    📤 Response ví dụ (HTTP 200):
    {
        "success": true,
        "message": "Lấy chi tiết đơn hàng thành công",
        "data": { ... dữ liệu đơn hàng ... }
    }

    📤 Response ví dụ (HTTP 502 - lỗi kết nối):
    {
        "success": false,
        "message": "Không gọi được dịch vụ chi tiết đơn hàng",
        "data": []
    }
    """
    def post(self, request):
        data = request.data.get("data") if isinstance(request.data, dict) and isinstance(request.data.get("data"), dict) else request.data
        ma_don_hang = data.get("ma_don_hang")
        api_url = f"{INTERNAL_API_BASE}/api/public/chi_tiet_don_hang/{ma_don_hang}"
        try:
            response = requests.get(api_url, timeout=30)
            return ApiResponse.success(
                message="Lấy chi tiết đơn hàng thành công" if response.ok else "Không lấy được chi tiết đơn hàng",
                data=response.json(),
                status=response.status_code
            )
        except requests.RequestException:
            return ApiResponse.error(
                message="Không gọi được dịch vụ chi tiết đơn hàng",
                status=502
            )


class OrderPaymentStatusView(APIView):
    """
    API kiểm tra trạng thái thanh toán đơn hàng.

    📌 Endpoint:
    POST /api/order/payment-status/

    📥 Request body ví dụ:
    {
        "ma_don_hang": "DH20251208195900"
    }

    📤 Response ví dụ (HTTP 200):
    {
        "success": true,
        "message": "Kiểm tra trạng thái thanh toán thành công",
        "data": {
            "paid": true,
            "remainder": 0
        }
    }
    """
    def post(self, request):
        if not isinstance(request.data, dict):
            return ApiResponse.error(
                message="Payload phải là JSON object",
                data={"payload": request.data},
                status=400
            )

        ma_don_hang = request.data.get("ma_don_hang") or request.data.get("order_id") or request.data.get("order_code")
        if not ma_don_hang:
            return ApiResponse.error(
                message="Thiếu mã đơn hàng",
                data={"payload": request.data},
                status=400
            )

        api_url = f"{INTERNAL_API_BASE}/api/public/chi_tiet_don_hang/{ma_don_hang}"

        def _to_number(value):
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0

        try:
            response = requests.get(api_url, timeout=30)
            downstream = response.json() if response.ok else {"raw": response.text}

            if not response.ok:
                return ApiResponse.error(
                    message="Không lấy được chi tiết đơn hàng",
                    data={"ma_don_hang": ma_don_hang, "downstream": downstream},
                    status=response.status_code
                )

            order_data = downstream.get("data") or {}
            if not isinstance(order_data, dict):
                order_data = {}
            tong_tien = _to_number(order_data.get("tong_tien"))
            tien_ck = _to_number(order_data.get("tien_ck"))
            tong_tien_ck = _to_number(order_data.get("tong_tien_chuyen_khoan"))

            remainder = tong_tien - tien_ck - tong_tien_ck
            paid = remainder == 0

            return ApiResponse.success(
                message="Kiểm tra trạng thái thanh toán thành công",
                data={"paid": paid, "remainder": remainder}
            )
        except requests.RequestException as exc:
            return ApiResponse.error(
                message="Không gọi được dịch vụ chi tiết đơn hàng",
                data={"error": str(exc), "ma_don_hang": ma_don_hang},
                status=502
            )


class OderPurchaseView(APIView):
    """
    API tạo đơn mua hàng.

    📌 Endpoint:
    POST /api/order/purchase/

    📥 Request body ví dụ:
    {
        "supplier_id": 1,
        "items": [
            {"product_id": "SP001", "quantity": 10}
        ]
    }

    📤 Response ví dụ (HTTP 200):
    {
        "success": true,
        "message": "Đơn mua đã được tạo thành công!",
        "data": []
    }
    """
    def post(self, request):
        order_data = request.data
        try:
            create_purchase_order_from_json(order_data)
            return ApiResponse.success(
                message="Đơn mua đã được tạo thành công!",
                data=[]
            )
        except Exception as e:
            return ApiResponse.error(
                message=f"Lỗi: {str(e)}",
                status=500
            )


class OderDepositView(APIView):
    """
    API tạo đơn đặt cọc.

    📌 Endpoint:
    POST /api/order/deposit/

    📥 Request body ví dụ:
    {
        "phone": "0987654321",
        "username_sale": "admin",
        "dien_giai": "Đặt cọc sản phẩm",
        "delivery_date": "2025-12-10",
        "sellorderitems": [
            {"product_id": "SP001", "quantity": 2}
        ]
    }

    📤 Response ví dụ (HTTP 200):
    {
        "success": true,
        "message": "Lên đơn đặt cọc thành công",
        "data": {
            "payload": { ... },
            "downstream": { ... }
        }
    }
    """
    deposit_url = f"{INTERNAL_API_BASE}/api/public/khachang_dat_coc"
    headers = {"Content-Type": "application/json; charset=utf-8"}

    def _normalize_payload(self, payload_source):
        data = payload_source["data"] if isinstance(payload_source, dict) and isinstance(payload_source.get("data"), dict) else payload_source
        ma_khachhang = data.get("phone", "").replace("*", "")
        if not ma_khachhang:
            raise ValueError("Thiếu thông tin mã khách hàng")

        manhanvien = data.get("username_sale")
        danh_sach = data.get("danh_sach") or []
        if not danh_sach:
            source_items = data.get("orderitems") or data.get("sellorderitems") or []
            for item in source_items:
                mahang = item.get("product_id")
                soluong = item.get("quantity")
                try:
                    soluong_val = float(soluong)
                except (TypeError, ValueError):
                    continue
                if mahang and soluong_val > 0:
                    danh_sach.append({"mahang": str(mahang), "soluong": soluong_val})

        if not danh_sach:
            raise ValueError("Thiếu danh sách sản phẩm")

        payload = {
            "ma_khachhang": ma_khachhang,
            "manhanvien": manhanvien,
            "dien_giai": data.get("dien_giai", ""),
            "ngay_giao": data.get("delivery_date", ""),
            "danh_sach": danh_sach
        }
        return data, payload

    def post(self, request):
        try:
            normalized_data, downstream_payload = self._normalize_payload(request.data)
        except ValueError as exc:
            return ApiResponse.error(
                message=str(exc),
                data={"payload": request.data},
                status=400
            )

        try:
            create_deposit_order_from_json(normalized_data)
        except Exception as e:
            return ApiResponse.error(
                message=f"Lỗi: {str(e)}",
                status=500
            )

        try:
            response = requests.post(self.deposit_url, headers=self.headers, json=downstream_payload, timeout=30)
            downstream = response.json() if response.ok else {"raw": response.text}
            return ApiResponse.success(
                message="Lên đơn đặt cọc thành công" if response.ok else "Trả lỗi",
                data={"payload": downstream_payload, "downstream": downstream},
                status=response.status_code
            )
        except requests.RequestException as exc:
            return ApiResponse.error(
                message="Không gọi được dịch vụ đặt cọc",
                data={"error": str(exc), "payload": downstream_payload},
                status=502
            )

class OderServiceView(APIView):
    """
    API tạo đơn dịch vụ.

    📌 Endpoint:
    POST /api/order/service/

    📥 Request body ví dụ:
    {
        "customer_id": 1,
        "service_type": "Bảo hành",
        "items": [
            {"product_id": "SP001", "quantity": 1}
        ]
    }

    📤 Response ví dụ (HTTP 200):
    {
        "success": true,
        "message": "Đơn dịch vụ đã được tạo thành công!",
        "data": []
    }

    📤 Response ví dụ (HTTP 500 - lỗi hệ thống):
    {
        "success": false,
        "message": "Lỗi: Không thể tạo đơn dịch vụ",
        "data": []
    }
    """
    def post(self, request):
        order_data = request.data
        try:
            create_service_order_from_json(order_data)
            return ApiResponse.success(
                message="Đơn dịch vụ đã được tạo thành công!",
                data=[]
            )
        except Exception as e:
            return ApiResponse.error(
                message=f"Lỗi: {str(e)}",
                status=500
            )


class WarehouseExportView(APIView):
    """
    API xuất kho.

    📌 Endpoint:
    POST /api/warehouse/export/

    📥 Request body ví dụ:
    {
        "ma_hoa_don": "HD20251208195900",
        "items": [
            {"product_id": "SP001", "quantity": 2}
        ]
    }

    📤 Response ví dụ (HTTP 200):
    {
        "success": true,
        "message": "Xuất kho thành công",
        "data": {
            "payload": { ... },
            "downstream": { ... }
        }
    }

    📤 Response ví dụ (HTTP 400 - thiếu mã hóa đơn):
    {
        "success": false,
        "message": "Thiếu mã hóa đơn",
        "data": { "payload": { ... } }
    }

    📤 Response ví dụ (HTTP 502 - lỗi kết nối):
    {
        "success": false,
        "message": "Không kết nối được dịch vụ xuất kho",
        "data": { "error": "Timeout", "payload": { ... } }
    }
    """
    export_url = f"{INTERNAL_API_BASE}/api/public/Xuat_kho"
    headers = {"Content-Type": "application/json; charset=utf-8"}

    def post(self, request):
        if not isinstance(request.data, dict):
            return ApiResponse.error(
                message="Payload phải là JSON object",
                data={"payload": request.data},
                status=400
            )

        data = request.data
        ma_hoa_don = data.get("ma_hoa_don") or data.get("mahoadon") or data.get("order_code") or data.get("order_id")
        if not ma_hoa_don:
            return ApiResponse.error(
                message="Thiếu mã hóa đơn",
                data={"payload": data},
                status=400
            )

        payload = {**data, "ma_hoa_don": ma_hoa_don}

        try:
            response = requests.post(self.export_url, headers=self.headers, json=payload, timeout=30)
            downstream = response.json() if response.ok else {"raw": response.text}
            return ApiResponse.success(
                message="Xuất kho thành công" if response.ok else "Xuất kho thất bại",
                data={"payload": payload, "downstream": downstream},
                status=response.status_code
            )
        except requests.RequestException as exc:
            return ApiResponse.error(
                message="Không kết nối được dịch vụ xuất kho",
                data={"error": str(exc), "payload": payload},
                status=502
            )


class ProductDiscountView(APIView):

    pg_host = getattr(settings, "EMAILTCKT_PG_HOST", "192.168.0.221")
    pg_port = int(getattr(settings, "EMAILTCKT_PG_PORT", 5432))
    pg_db = getattr(settings, "EMAILTCKT_PG_DB", "EmailTCKT")
    pg_user = getattr(settings, "EMAILTCKT_PG_USER", "postgres")
    pg_password = getattr(settings, "EMAILTCKT_PG_PASSWORD", "admin")

    # Downstream price API
    price_api_base = getattr(settings, "PRICE_API_BASE", "http://192.168.0.223:8096")

    def _parse_percent(self, raw_value):
        if raw_value is None:
            return 0.0
        try:
            text = str(raw_value).strip()
            if text.endswith("%"):
                text = text[:-1]
            text = text.replace(" ", "").replace(",", ".")
            val = float(text)
            if val > 1:
                val = val / 100.0
            if val < 0:
                val = 0.0
            if val > 1:
                val = 1.0
            return val
        except (ValueError, TypeError):
            return 0.0

    def _get_discount_rate(self, ma_hang):
        conn = None
        try:
            conn = psycopg2.connect(
                host=self.pg_host,
                port=self.pg_port,
                dbname=self.pg_db,
                user=self.pg_user,
                password=self.pg_password,
                connect_timeout=5,
            )
            with conn, conn.cursor() as cur:
                cur.execute(
                    'SELECT "phan_tram_giam_gia" FROM "CTKM_NgoQuyen" WHERE "Ma_hang" = %s LIMIT 1',
                    (ma_hang,)
                )
                row = cur.fetchone()
                if not row:
                    return 0.0
                return self._parse_percent(row[0])
        except Exception:
            # Nếu lỗi kết nối/đọc, báo 502 phía trên
            raise
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def _get_base_price(self, ma_hang):
        url = f"{self.price_api_base}/api/public/hang_ma_kho/{ma_hang}/GH1"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json().get("data") if resp.headers.get("Content-Type", "").startswith("application/json") else None
            if not isinstance(data, dict):
                return None
            gia = data.get("giaBan")
            if gia is None:
                return None
            try:
                return float(gia)
            except (TypeError, ValueError):
                return None
        except requests.RequestException:
            raise

    def post(self, request):
        if not isinstance(request.data, dict):
            return ApiResponse.error(
                message="Payload phải là JSON object",
                data=[{"payload": request.data}],
                status=400
            )

        ma_hang = request.data.get("ma_hang")
        if not ma_hang:
            return ApiResponse.error(
                message="Thiếu mã hàng",
                data=[{"payload": request.data}],
                status=400
            )

        try:
            discount_rate = self._get_discount_rate(ma_hang)
        except Exception as exc:
            return ApiResponse.error(
                message="Không đọc được chiết khấu từ Postgres",
                data=[{"error": str(exc), "ma_hang": ma_hang}],
                status=502
            )

        try:
            base_price = self._get_base_price(ma_hang)
        except Exception as exc:
            return ApiResponse.error(
                message="Không lấy được giá bán từ SQL Server",
                data=[{"error": str(exc), "ma_hang": ma_hang}],
                status=502
            )

        if base_price is None:
            return ApiResponse.error(
                message="Không tìm thấy giá bán cho mã hàng",
                data=[{"ma_hang": ma_hang}],
                status=404
            )

        so_tien_ck = round(base_price * discount_rate, 0)

        return ApiResponse.success(
            message="Thành công",
            data=[{
                "ma_hang": ma_hang,
                "tong_tien_chua_ck": base_price,
                "so_tien_ck": so_tien_ck,
                "CTKM": "Giảm giá theo danh mục CTKM Khai trương Ngô Quyền"
            }]
        )


class ProductDiscountViewAugges(APIView):
    """
    Lấy danh sách CTKM từ Augges rồi tính chiết khấu cho danh sách mã hàng đầu vào.

    - Bước 1: GET http://192.168.0.223:8097/api/public/CTKM => lấy list id CTKM
    - Bước 2: POST http://192.168.0.223:8869/api/public/all_ctmk với payload:
        {
            "ma_hang": <list từ body request hiện tại>,
            "ma_ct": <list id bước 1>,
            "ma_nhanvien": "",
            "ma_khach_hang": ""
        }
    - Trả nguyên downstream response cho client.
    """

    promo_url = "http://192.168.0.223:8097/api/public/CTKM"
    discount_url = "http://192.168.0.223:8869/api/public/all_ctmk"
    headers = {"Content-Type": "application/json; charset=utf-8"}

    def _normalize_ma_hang(self, raw):
        if raw is None:
            return []
        if isinstance(raw, str):
            return [raw]
        if isinstance(raw, (list, tuple)):
            return list(raw)
        return []

    def post(self, request):
        if not isinstance(request.data, dict):
            return ApiResponse.error(
                message="Payload phải là JSON object",
                data=[{"payload": request.data}],
                status=400
            )

        ma_hang = self._normalize_ma_hang(request.data.get("ma_hang"))
        if not ma_hang:
            return ApiResponse.error(
                message="Thiếu ma_hang (list)",
                data=[{"payload": request.data}],
                status=400
            )

        try:
            promo_resp = requests.get(self.promo_url, timeout=10)
            promo_resp.raise_for_status()
            promo_json = promo_resp.json()
        except requests.RequestException as exc:
            return ApiResponse.error(
                message="Không gọi được dịch vụ CTKM",
                data=[{"error": str(exc)}],
                status=502
            )
        except ValueError:
            return ApiResponse.error(
                message="CTKM trả về dữ liệu không phải JSON",
                data=[{"raw": getattr(promo_resp, "text", None)}],
                status=502
            )

        data_list = promo_json.get("data") if isinstance(promo_json, dict) else None
        ma_ct = [item.get("id") for item in data_list or [] if isinstance(item, dict) and item.get("id") is not None]

        if not ma_ct:
            return ApiResponse.error(
                message="Không tìm thấy chương trình khuyến mãi nào",
                data=[{"downstream": promo_json}],
                status=404
            )

        payload = {
            "ma_hang": ma_hang,
            "ma_ct": ma_ct,
            "ma_nhanvien": request.data.get("ma_nhanvien", ""),
            "ma_khach_hang": request.data.get("ma_khach_hang", ""),
        }

        try:
            discount_resp = requests.post(
                self.discount_url,
                headers=self.headers,
                json=payload,
                timeout=15
            )
        except requests.RequestException as exc:
            return ApiResponse.error(
                message="Không gọi được dịch vụ tính chiết khấu",
                data=[{"error": str(exc), "payload": payload}],
                status=502
            )

        try:
            downstream = discount_resp.json()
        except ValueError:
            downstream = {"raw": discount_resp.text}

        return ApiResponse.success(
            message="Thành công" if discount_resp.ok else "Không tính được chiết khấu",
            data=[{"downstream": downstream, "payload": payload}],
            status=discount_resp.status_code
        )


class ProductDiscountBestView(APIView):
    """
    Kết hợp chiết khấu nội bộ (Postgres + giá kho) và chiết khấu Augges.
    - Tính chiết khấu nội bộ giống ProductDiscountView.
    - Gọi Augges giống ProductDiscountViewAugges.
    - So sánh số tiền chiết khấu, trả về phương án có giá trị cao hơn.
    - Chỉ trả lỗi khi cả hai nguồn đều lỗi.
    """

    product_discount = ProductDiscountView()
    promo_url = ProductDiscountViewAugges.promo_url
    discount_url = ProductDiscountViewAugges.discount_url
    headers = ProductDiscountViewAugges.headers

    def _normalize_ma_hang(self, raw):
        if raw is None:
            return []
        if isinstance(raw, str):
            return [raw]
        if isinstance(raw, (list, tuple)):
            return list(raw)
        return []

    def _calc_internal(self, ma_hang: str):
        try:
            rate = self.product_discount._get_discount_rate(ma_hang)
            base = self.product_discount._get_base_price(ma_hang)
            if base is None:
                return {"ok": False, "amount": 0, "reason": "no_base_price"}
            return {"ok": True, "amount": round(base * rate, 0), "base_price": base, "rate": rate}
        except Exception as exc:  # pragma: no cover - defensive
            return {"ok": False, "amount": 0, "reason": str(exc)}

    def _calc_augges(self, ma_hang_list, ma_nhanvien: str, ma_khach_hang: str):
        try:
            promo = requests.get(self.promo_url, timeout=10)
            promo.raise_for_status()
            promo_json = promo.json()
            ma_ct = [it.get("id") for it in (promo_json.get("data") or []) if isinstance(it, dict) and it.get("id") is not None]
        except Exception as exc:  # pragma: no cover - defensive
            return {"ok": False, "amount": 0, "reason": f"ctkm_error: {exc}"}

        if not ma_ct:
            return {"ok": False, "amount": 0, "reason": "no_ctkm"}

        payload = {
            "ma_hang": ma_hang_list,
            "ma_ct": ma_ct,
            "ma_nhanvien": ma_nhanvien,
            "ma_khach_hang": ma_khach_hang,
        }

        try:
            resp = requests.post(self.discount_url, headers=self.headers, json=payload, timeout=15)
            try:
                downstream = resp.json()
            except ValueError:
                downstream = {"raw": resp.text}
        except Exception as exc:  # pragma: no cover - defensive
            return {"ok": False, "amount": 0, "reason": f"discount_error: {exc}"}

        amount = 0
        if isinstance(downstream, dict):
            data_items = downstream.get("data")
            if isinstance(data_items, list):
                vals = []
                for item in data_items:
                    if isinstance(item, dict):
                        try:
                            vals.append(float(item.get("tienCk", 0) or 0))
                        except (TypeError, ValueError):
                            continue
                if vals:
                    amount = max(vals)

        ok = amount > 0 or resp.ok if 'resp' in locals() else False
        return {"ok": ok, "amount": amount, "downstream": downstream}

    def post(self, request):
        if not isinstance(request.data, dict):
            return ApiResponse.error(
                message="Payload phải là JSON object",
                data=[{"payload": request.data}],
                status=400
            )

        ma_hang_list = self._normalize_ma_hang(request.data.get("ma_hang"))
        if not ma_hang_list:
            return ApiResponse.error(
                message="Thiếu ma_hang",
                data=[{"payload": request.data}],
                status=400
            )

        internal = self._calc_internal(ma_hang_list[0])
        augges = self._calc_augges(
            ma_hang_list,
            request.data.get("ma_nhanvien", ""),
            request.data.get("ma_khach_hang", ""),
        )

        candidates = [("internal", internal), ("augges", augges)]
        ok_candidates = [(src, data) for src, data in candidates if data.get("ok")]

        if not ok_candidates:
            return ApiResponse.error(
                message="Cả hai nguồn chiết khấu đều lỗi",
                data=[{"internal": internal, "augges": augges}],
                status=502
            )

        best_source, best_data = max(ok_candidates, key=lambda item: item[1].get("amount", 0))

        return ApiResponse.success(
            message="Success",
            data=[{
                "best_source": best_source,
                "best_amount": best_data.get("amount", 0),
                "internal": internal,
                "augges": augges
            }]
        )


class BasePriceRawView(APIView):
    price_api_base = getattr(settings, "PRICE_API_BASE", "http://192.168.0.223:8096")

    def get(self, request):
        ma_hang = request.query_params.get("ma_hang")
        if not ma_hang:
            return ApiResponse.error(
                message="Thiếu mã hàng",
                data=[],
                status=400
            )

        url = f"{self.price_api_base}/api/public/hang_ma_kho/{ma_hang}/FS01"

        try:
            resp = requests.get(url, timeout=10)
        except requests.RequestException as exc:
            return ApiResponse.error(
                message="Không gọi được dịch vụ giá",
                data=[{"error": str(exc), "ma_hang": ma_hang}],
                status=502
            )

        content_type = resp.headers.get("Content-Type", "")
        if content_type.startswith("application/json"):
            try:
                payload = resp.json()
            except ValueError:
                payload = {"raw": resp.text}
        else:
            payload = {"raw": resp.text}

        if resp.ok:
            return ApiResponse.success(
                message="Lấy giá gốc thành công",
                data=[payload],
                status=resp.status_code
            )
        return ApiResponse.error(
            message="Không lấy được giá gốc",
            data=[payload],
            status=resp.status_code
        )


class PaymentConfirmView(APIView):
    """
    API xác nhận thanh toán.

    📌 Endpoint:
    POST /api/payment/confirm/

    📥 Request body ví dụ:
    {
        "ma_hoa_don": "HD20251208195900",
        "so_tien": 500000,
        "loai": 1
    }

    📤 Response ví dụ (HTTP 200):
    {
        "success": true,
        "message": "Thanh toán thành công 500000 VND",
        "data": {
            "payload": { ... },
            "downstream": { ... }
        }
    }

    📤 Response ví dụ (HTTP 400 - thiếu trường):
    {
        "success": false,
        "message": "Thiếu trường bắt buộc",
        "data": { "fields": ["ma_hoa_don", "so_tien"], "payload": { ... } }
    }
    """
    payment_url = f"{INTERNAL_API_BASE}/api/public/Thanh_toan"
    headers = {"Content-Type": "application/json; charset=utf-8"}

    def post(self, request):
        if not isinstance(request.data, dict):
            return ApiResponse.error(
                message="Payload phải là JSON object",
                data={"payload": request.data},
                status=400
            )

        data = request.data
        ma_hoa_don = data.get("ma_hoa_don")
        so_tien = data.get("so_tien")
        loai = data.get("loai")

        missing = []
        if not ma_hoa_don:
            missing.append("ma_hoa_don")
        if so_tien in (None, ""):
            missing.append("so_tien")
        if loai in (None, ""):
            missing.append("loai")

        if missing:
            return ApiResponse.error(
                message="Thiếu trường bắt buộc",
                data={"fields": missing, "payload": data},
                status=400
            )

        payload = {**data, "ma_hoa_don": ma_hoa_don, "so_tien": so_tien, "loai": loai}

        try:
            response = requests.post(self.payment_url, headers=self.headers, json=payload, timeout=30)
            downstream = response.json() if response.ok else {"raw": response.text}
            return ApiResponse.success(
                message=f"Thanh toán thành công {so_tien} VND" if response.ok else "Thanh toán thất bại",
                data={"payload": payload, "downstream": downstream},
                status=response.status_code
            )
        except requests.RequestException as exc:
            return ApiResponse.error(
                message="Không kết nối được dịch vụ thanh toán",
                data={"error": str(exc), "payload": payload},
                status=502
            )


class OrderReplaceView(APIView):
    """
    API tạo đơn đổi hàng.

    📌 Endpoint:
    POST /api/order/replace/

    📥 Request body ví dụ:
    {
        "customer_id": 1,
        "items": [
            {"product_id": "SP001", "quantity": 1}
        ]
    }

    📤 Response ví dụ (HTTP 200):
    {
        "success": true,
        "message": "Đơn Đổi hàng đã được tạo thành công!",
        "data": []
    }
    """
    def post(self, request):
        order_data = request.data
        try:
            create_replace_order_from_json(order_data)
            return ApiResponse.success(
                message="Đơn Đổi hàng đã được tạo thành công!",
                data=[]
            )
        except Exception as e:
            return ApiResponse.error(
                message=f"Lỗi: {str(e)}",
                status=500
            )


class ProductImageView(APIView):
    """
    API lấy ảnh sản phẩm.

    📌 Endpoint:
    POST /api/product/image/

    📥 Request body ví dụ:
    {
        "serial": "SP001"
    }

    📤 Response ví dụ (HTTP 200):
    {
        "success": true,
        "message": "Lấy ảnh sản phẩm thành công",
        "data": { ... chi tiết ảnh ... }
    }
    """
    def post(self, request):
        serial = request.data.get("serial")
        if not serial:
            return ApiResponse.error(message="Thiếu mã sản phẩm", status=400)

        try:
            response = requests.post(
                "https://14.224.192.52:9999/api/v1/product-images",
                json={"ma_hang": serial},
                cert=cert,
                verify=CA_CERT_PATH
            )
            detail = response.json()
            return ApiResponse.success(
                message="Lấy ảnh sản phẩm thành công",
                data=detail
            )
        except requests.RequestException as exc:
            return ApiResponse.error(
                message="Không kết nối được dịch vụ ảnh sản phẩm",
                data={"error": str(exc), "serial": serial},
                status=502
            )
