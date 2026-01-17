
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
# import pandas as pd
# from .tasks import poll_payment_and_confirm
import requests
from apps.common.utils.api_response import ApiResponse   # <-- class chuẩn hóa response
from apps.store.syncodoo import OdooClient, ApiClient, ProductTemplate, ProductSyncService

odoo_client = OdooClient(
    base_url=settings.ODOO_SERVER_URL,
    db=settings.ODOO_DB,
    username=settings.ODOO_USERNAME,
    password=settings.ODOO_PASSWORD,
)

# 2. Khởi tạo ApiClient (dùng INTERNAL_API_BASE trong settings)
api_client = ApiClient()

# 3. (Tùy chọn) Khởi tạo helper ProductTemplate nếu cần gọi trực tiếp
product_helper = ProductTemplate(odoo=odoo_client)

# 4. Khởi tạo service đồng bộ
sync_service = ProductSyncService(odoo_client, api_client)

class SerialRawView(APIView):
    price_api_base = settings.INTERNAL_API_BASE

    def get(self, request):
        code = request.query_params.get("code")
        ma_kho = request.query_params.get("inventory", "FS01")
        if not code:
            return ApiResponse.error(
                message="Thiếu mã hàng",
                data=[],
                status=400
            )

        # run_sync.py
        try:
            result = sync_service.sync_product_and_serial(code, ma_kho)

            return ApiResponse.success(
                message="Serial thanh cong",
                data=result,
                status=200
            )
        except Exception as ex:
            return ApiResponse.error(
                message="Xay ra su co",
                data=result,
                status=400
            )

