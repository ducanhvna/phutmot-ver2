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
import requests
import json

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
    qr_url = f"{INTERNAL_API_BASE}/api/public/QRcode"
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }

    def post(self, request):
        data = request.data
        id_don = data.get("id_don")
        payload = {
            "taikhoanthuhuong": data.get("taikhoanthuhuong"),
            "noichuyentien": data.get("noidungchuyentien", f"{id_don} - APPSALE"),
            "sotien": data.get("sotien")
        }
        
        missing = [key for key, value in payload.items() if value in (None, "")]
        if missing:
            return Response({
                "status": 400,
                "msg": "Thiếu trường bắt buộc",
                "fields": missing
            }, status=400)

        try:
            response = requests.post(self.qr_url, headers=self.headers, json=payload, timeout=30)
            try:
                downstream = response.json()
            except ValueError:
                downstream = {"raw": response.text}

            return Response({
                "status": response.status_code,
                "msg": "Thành công" if response.ok else "Thất bại",
                "data": response.json()
            }, status=response.status_code)
        except requests.RequestException as exc:
            return Response({
                "status": 502,
                "msg": "Không kết nối được dịch vụ QR",
                "error": str(exc),
                "payload": payload
            }, status=502)
    
class OrderSellView(APIView):
    def post(self, request):
        order_data = request.data
        try:
            create_order_from_json(order_data)
            return Response({
                "status": 200,
                "msg": "Đơn hàng đã được tạo thành công!"
            })
        except Exception as e:
            return Response({"status": 500, "msg": str(e)}, status=500)

class OrderShellView(APIView):
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

        ma_khachhang = data.get("ma_khachhang")

        if not ma_khachhang:
            ma_khachhang = data.get("phone", "").replace("*", "")

        if not ma_khachhang:
            return Response({
                "status": 400,
                "msg": "Thiếu thông tin mã khách hàng",
                "details": {
                    "payload": data
                }
            }, status=400)

        danh_sach = data.get("danh_sach") or []
        if not danh_sach:
            items = data.get("sellorderitems", [])
            for item in items:
                product_id = item.get("product_id")
                if product_id is None:
                    continue
                danh_sach.append({
                    "mahang": str(product_id),
                    "soluong": item.get("quantity", 1)
                })

        if not danh_sach:
            return Response({
                "status": 400,
                "msg": "Thiếu danh sách sản phẩm",
                "details": {
                    "payload": data,
                    "sellorderitems": data.get("sellorderitems", [])
                }
            }, status=400)

        payload = {
            "ma_khachhang": ma_khachhang,
            "manhanvien": data.get("username_sale", ""),
            "dien_giai": data.get("dien_giai", ""),
            "danh_sach": danh_sach
        }

        try:
            # response = requests.post(self.order_url, headers=self.headers, data=json.dumps(payload))
            response = requests.post(self.order_url, headers=self.headers, json=payload, timeout=30)
            print(response.text)
            try:
                body = response.json()
            except ValueError:
                body = {"raw": response.text}

            return Response({
                "status": response.status_code,
                "success": response.ok,
                "msg": response.json().get('data') if response.ok else "Tạo đơn hàng thất bại",
                "downstream": body,
                "payload": payload
            }, status=response.status_code)
        except requests.RequestException as exc:
            return Response({
                "status": 502,
                "msg": "Không gọi được dịch vụ đích",
                "error": str(exc),
                "payload": payload
            }, status=502)
        
class OderPurchaseView(APIView):
    def post(self, request):
        order_data = request.data
        try:
            create_purchase_order_from_json(order_data)
            return Response({
                "status": 200,
                "msg": "Đơn mua đã được tạo thành công!"
            })
        except Exception as e:
            return Response({"status": 500, "msg": str(e)}, status=500)
                
class OderDepositView(APIView):
    deposit_url = f"{INTERNAL_API_BASE}/api/public/khachang_dat_coc"
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }

    def _normalize_payload(self, payload_source):
        if isinstance(payload_source, dict) and isinstance(payload_source.get("data"), dict):
            data = payload_source["data"]
        else:
            data = payload_source

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
                if not mahang or soluong in (None, ""):
                    continue
                try:
                    soluong_val = float(soluong)
                except (TypeError, ValueError):
                    continue
                if soluong_val <= 0:
                    continue
                danh_sach.append({
                    "mahang": str(mahang),
                    "soluong": soluong_val
                })

        danh_sach = [entry for entry in danh_sach if entry.get("mahang") and entry.get("soluong")]
        if not danh_sach:
            raise ValueError("Thiếu danh sách sản phẩm")

        ngay_giao = data.get('delivery_date', '')

        payload = {
            "ma_khachhang": ma_khachhang,
            "manhanvien": manhanvien,
            "dien_giai": data.get("dien_giai", ""),
            "ngay_giao": ngay_giao,
            "danh_sach": danh_sach
        }

        return data, payload

    def post(self, request):
        try:
            normalized_data, downstream_payload = self._normalize_payload(request.data)
        except ValueError as exc:
            return Response({
                "status": 400,
                "msg": str(exc),
                "payload": request.data
            }, status=400)

        try:
            create_deposit_order_from_json(normalized_data)
        except Exception as e:
            return Response({"status": 500, "msg": str(e)}, status=500)

        try:
            response = requests.post(
                self.deposit_url,
                headers=self.headers,
                json=downstream_payload,
                timeout=30
            )
            try:
                downstream = response.json()
            except ValueError:
                downstream = {"raw": response.text}

            return Response({
                "status": response.status_code,
                "success": response.ok,
                "msg": "Lên đơn đặt cọc thành công" if response.ok else "Trả lỗi",
                "payload": downstream_payload,
                "downstream": downstream
            }, status=response.status_code)
        except requests.RequestException as exc:
            return Response({
                "status": 502,
                "msg": "Không gọi được dịch vụ đặt cọc",
                "error": str(exc),
                "payload": downstream_payload
            }, status=502)
 

class OderServiceView(APIView):
    def post(self, request):
        order_data = request.data
        try:
            create_service_order_from_json(order_data)
            return Response({
                "status": 200,
                "msg": "Đơn dịch vụ đã được tạo thành công!"
            })
        except Exception as e:
            return Response({"status": 500, "msg": str(e)}, status=500)


class WarehouseExportView(APIView):
    export_url = f"{INTERNAL_API_BASE}/api/public/Xuat_kho"
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }

    def post(self, request):
        if isinstance(request.data, dict):
            data = request.data
        else:
            return Response({
                "status": 400,
                "msg": "Payload phải là JSON object",
                "payload": request.data
            }, status=400)

        ma_hoa_don = (
            data.get("ma_hoa_don")
            or data.get("mahoadon")
            or data.get("order_code")
            or data.get("order_id")
        )

        if not ma_hoa_don:
            return Response({
                "status": 400,
                "msg": "Thiếu mã hóa đơn",
                "payload": data
            }, status=400)

        payload = {**data, "ma_hoa_don": ma_hoa_don}

        try:
            response = requests.post(
                self.export_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            try:
                downstream = response.json()
            except ValueError:
                downstream = {"raw": response.text}

            return Response({
                "status": response.status_code,
                "success": response.ok,
                "msg": "Xuất kho thành công" if response.ok else "Xuất kho thất bại",
                "payload": payload,
                "downstream": downstream
            }, status=response.status_code)
        except requests.RequestException as exc:
            return Response({
                "status": 502,
                "msg": "Không kết nối được dịch vụ xuất kho",
                "error": str(exc),
                "payload": payload
            }, status=502)


class OrderReplaceView(APIView):
    def post(self, request):
        order_data = request.data
        try:
            create_replace_order_from_json(order_data)
            return Response({
                "status": 200,
                "msg": "Đơn Đổi hàng đã được tạo thành công!"
            })
        except Exception as e:
            return Response({"status": 500, "msg": str(e)}, status=500)

class ProductImageView(APIView):
    def post(self, request):
        # account_type = request.data.get("account_type")
        # account_no = request.data.get("account_no")
        serial = request.data.get("serial")
        
        response = requests.post(
            "https://14.224.192.52:9999/api/v1/product-images",
            json={
                "ma_hang": serial
            },
            cert=cert,
            verify= CA_CERT_PATH # hoặc verify=False nếu chỉ test
        )
        detail = response.json()
        return Response({
            "status": 200,
            "msg": "Successfully",
            "data": detail
        })