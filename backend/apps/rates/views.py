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