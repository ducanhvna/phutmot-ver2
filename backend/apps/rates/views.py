from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from apps.store.authentication import JWTAuthentication
# import pandas as pd
from apps.store.data_loader import cert, CA_CERT_PATH
import math
import numpy as np
import datetime
# from .ordersell import create_order_from_json
# from .orderpurchase import create_purchase_order_from_json
# from .orderdeposit import create_deposit_order_from_json
# from .orderservice import create_service_order_from_json
# from .orderreplace import create_replace_order_from_json
# from .tasks import poll_payment_and_confirm
import requests
import json
from base64 import b64encode
from urllib.parse import urlencode
import psycopg2
from apps.home.utils import ApiResponse   # <-- class chuẩn hóa response
from rest_framework.pagination import PageNumberPagination
import os
import uuid
from django.utils import timezone

# Lấy tỷ giá từ nguồn bên ngoài
# url_tygia_k = "https://14.224.192.52:9999/api/v1/tigia?that=0"
# response = requests.get(
#     url_tygia_k, 
#     verify=False) # hoặc verify=False nếu chỉ test
# tygia_k_data = response.json()
# [
#     {'tenToChuc': 'Công ty cổ phần Bảo Tín Mạnh Hải', 'loaiVang': 'Vàng 10K S.phẩm Công nghệ', 'khoiLuong': '', 'maLoaivang': '10K-CN', 'giaMuaNiemYet': 3950000.0, 'giaBanNiemYet': 3950000.0, 'donViTinh': 'VND', 'ngayCapNhat': '2022-06-27 16: 24: 03.027'
#     },
#     ......
#     {'tenToChuc': 'Công ty cổ phần Bảo Tín Mạnh Hải', 'loaiVang': 'Vàng miếng SJC (Cty CP BTMH)', 'khoiLuong': '', 'maLoaivang': 'SJC', 'giaMuaNiemYet': 14760000.0, 'giaBanNiemYet': 14900000.0, 'donViTinh': 'VND', 'ngayCapNhat': '2025-11-03 15: 53: 19.130'
#     },
#     {'tenToChuc': 'Công ty cổ phần Bảo Tín Mạnh Hải', 'loaiVang': 'Nhẫn ép vỉ Vàng Rồng Thăng Long', 'khoiLuong': '', 'maLoaivang': 'VRTL', 'giaMuaNiemYet': 14650000.0, 'giaBanNiemYet': 1.0, 'donViTinh': 'VND', 'ngayCapNhat': '2025-11-03 17: 18: 53.377'
#     }
# ]

class RateView(APIView):
    """
    Lấy tỷ giá sản phẩm
    """
    authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            url_tygia_k = "https://14.224.192.52:9999/api/v1/tigia?that=0"
            response = requests.get(
                url_tygia_k, 
                verify=False) # hoặc verify=False nếu chỉ test
            tygia_data = response.json()
            # Thêm 1 trường tỷ giá tham chiếu vào mỗi mục
            for item in tygia_data:
                item['TyGia_ThamChieu'] = ((item['giaMuaNiemYet'] + item['giaBanNiemYet']) / 2)
            return ApiResponse.success(data=tygia_data)
        except Exception as e:
            return ApiResponse.error(message=str(e))
        
# làm 1 api chuyển tiếp việc gọi API update tỷ giá như sau:
# BASE_URL = os.getenv("API_BASE_URL", "https://14.224.192.52:9999")
# url = f"{BASE_URL}/api/v1/tigia/update"
# # that: 0=DB chính, 1=DB khác (cần cấu hình tvf_db_dsn)
# THAT = int(os.getenv("TIGIA_THAT", "0"))
# payload = {
#     "ma_vbtg": "9999",          # đổi mã theo DmVBTG
#     "ty_gia_mua_cu": 31000,      # nếu sai -> API trả 409 và trả về current để bạn copy
#     "ty_gia_ban_cu": 34000,      # nếu sai -> API trả 409 và trả về current để bạn copy
#     "ty_gia_mua": 30000,
#     "ty_gia_ban": 34000,
#     "that": 1,
# }
# r = requests.post(url, json=payload, timeout=30, verify=False)
# print("URL:", url)
# print("Status:", r.status_code)
# try:
#     data = r.json()
#     print(json.dumps(data, ensure_ascii=False, indent=2))
# except Exception:
#     print(r.text)
#     raise 

class RateUpdateView(APIView):
    """
    Cập nhật tỷ giá sản phẩm
    """
    authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            BASE_URL = os.getenv("API_BASE_URL", "https://14.224.192.52:9999")
            url = f"{BASE_URL}/api/v1/tigia/update"
            # that: 0=DB chính, 1=DB khác (cần cấu hình tvf_db_dsn)
            THAT = int(os.getenv("TIGIA_THAT", "0"))       
            danh_sach_cap_nhat = request.data.get("rates", [])
            results = []
            for item in danh_sach_cap_nhat:
                ma_vbtg = None
                try:
                    ma_vbtg = item.get("ma_vbtg")
                    ty_gia_mua_cu = item.get("ty_gia_mua_cu")
                    ty_gia_ban_cu = item.get("ty_gia_ban_cu")
                    ty_gia_mua = item.get("ty_gia_mua")             
                    ty_gia_ban = item.get("ty_gia_ban")
                    payload = {     
                        "ma_vbtg": ma_vbtg,          # đổi mã theo DmVBTG
                        "ty_gia_mua_cu": ty_gia_mua_cu,      # nếu sai -> API trả 409 và trả về current để bạn copy
                        "ty_gia_ban_cu": ty_gia_ban_cu,      # nếu sai -> API trả 409 và trả về current để bạn copy
                        "ty_gia_mua": ty_gia_mua,
                        "ty_gia_ban": ty_gia_ban,
                        "that": THAT,
                    }
                    r = requests.post(url, json=payload, timeout=30, verify=False)
                    if r.status_code == 200:        
                        data = r.json()
                        results.append({
                            "ma_vbtg": ma_vbtg,
                            "status": "success",
                            "data": data
                        })
                    else:
                        results.append({
                            "ma_vbtg": ma_vbtg,
                            "status": "error",
                            "message": f"Error {r.status_code}: {r.text}"
                        })   
                except Exception as e:
                    results.append({
                        "ma_vbtg": ma_vbtg,
                        "status": "error",
                        "message": str(e)
                    })

            return ApiResponse.success(data=results, message="Cập nhật tỷ giá hoàn tất")
        except Exception as e:
            return ApiResponse.error(message=str(e))