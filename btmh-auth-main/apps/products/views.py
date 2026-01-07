
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
# import pandas as pd
import math
import numpy as np
import datetime
# from .tasks import poll_payment_and_confirm
import requests
import json
from base64 import b64encode
from urllib.parse import urlencode
import psycopg2
from apps.common.utils.api_response import ApiResponse   # <-- class chuẩn hóa response

class BasePriceRawView(APIView):
    price_api_base = settings.INTERNAL_API_BASE

    def get(self, request):
        ma_hang = request.query_params.get("sku")
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
            payload['data']['ton_kho'] = int(payload['data'].get('ton_kho', 0)) + 20
            return ApiResponse.success(
                message="Lấy giá gốc thành công",
                data=payload['data'],
                status=resp.status_code
            )
        return ApiResponse.error(
            message="Không lấy được giá gốc",
            data=payload,
            status=resp.status_code
        )
