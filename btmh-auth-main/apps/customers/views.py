import requests, json
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.exceptions import MethodNotAllowed
import re
from apps.common.utils.api_response import ApiResponse   # <-- class chuẩn hóa response
from django.conf import settings

INTERNAL_API_BASE = settings.INTERNAL_API_BASE
EXTERNAL_CUSTOMER_ADD_URL = f"{settings.INTERNAL_API_BASE}/api/public/khach_hang/add"
EXTERNAL_CUSTOMER_UPDATE_URL = f"{settings.INTERNAL_API_BASE}/api/public/khach_hang/update"
EXTERNAL_CUSTOMER_SEARCH_URL = f"{settings.INTERNAL_API_BASE}/api/public/khach_hang/timkiem"
EXTERNAL_CUSTOMER_POINTS = f"{settings.INTERNAL_API_BASE}/api/public/diem_khach_hang"
def is_phone_number(text: str) -> bool:
    # Số điện thoại Việt Nam thường có 10 chữ số, bắt đầu bằng 0 hoặc +84
    phone_pattern = re.compile(r"^(0\d{9}|\+84\d{9})$")
    return bool(phone_pattern.match(text))

def is_id_card(text: str) -> bool:
    # CMND cũ: 9 chữ số
    # CCCD mới: 12 chữ số
    id_pattern = re.compile(r"^\d{9}$|^\d{12}$")
    return bool(id_pattern.match(text))

# Header
headers = {
    "Content-Type": "application/json; charset=utf-8"
}

class PostOnlyAPIView(APIView):
    """APIViews that reject GET and only allow POST/OPTIONS."""

    http_method_names = ["post", "options"]

    def get(self, request, *args, **kwargs):  # pragma: no cover - explicit 405
        raise MethodNotAllowed("GET")

# Create your views here.
class CustomerSearchView(PostOnlyAPIView):
    """
    API tìm kiếm khách hàng.

    📥 Request body ví dụ:
    {
        "q": "0987654321",
        "name": "Nguyễn Văn B"
    }

    📤 Response ví dụ (HTTP 201):
    {
        "success": true,
        "message": "Tạo khách hàng thành công",
        "data": {
            "id": 2,
            "username": "0987654321",
            "name": "Nguyễn Văn B",
            "phone_number": "0987654321",
            "id_card_number": null,
            "email": ""
        }
    }

    📤 Response ví dụ (HTTP 400 - lỗi dữ liệu):
    {
        "success": false,
        "message": "Dữ liệu không hợp lệ",
        "data": []
    }
    """

    def post(self, request):
        incoming_data = request.data
        query = incoming_data.get("q", '').strip()

        if is_phone_number(query) or is_id_card(query):
            payload = {"sdt": query}
            response = requests.post(EXTERNAL_CUSTOMER_SEARCH_URL, headers=headers, data=json.dumps(payload), timeout=25)
            data = response.json()
            results = data.get("data", [])
            new_customer = None
            point_data = None
            if len(results)>0:
                try:
                    payload = {"tungay": 220101,
                                "dennay": 291201,
                                "sdt": query}
                    
                    response = requests.post(EXTERNAL_CUSTOMER_POINTS, headers=headers, data=json.dumps(payload), timeout=25)
                    point_data = response.json()
                except Exception as e2:
                    point_data = e2
                item = results[0]
                birth_date = item.get("ngay_sinh")
                new_customer = {
                    "username":item.get("dien_thoai"),
                    "name":item.get("ho_ten_khach_hang") or "",
                    "phone":item.get("dien_thoai") or "",
                    "id_card_number":item.get("cccd_cmt") or "",
                    "gender":"Male" if item.get("gioi_tinh") == "Nam" else "Female" if item.get("gioi_tinh") == "Nữ" else "",
                    "birth_date":birth_date.split(" ")[0] if birth_date else None,
                    "email":item.get("email") or "",
                    "address":{
                        "dia_chi": item.get("dia_chi"),
                        "tinh": item.get("tinh"),
                        "quan": item.get("quan"),
                        "phuong": item.get("phuong"),
                    },
                    "info":{
                        "ghi_chu": item.get("ghi_chu"),
                        "so_diem": item.get("so_diem"),
                        "hang": item.get("hang"),
                        "image_khach_hang": item.get("image_khach_hang"),
                        "qr_code": item.get("qr_code"),
                    },
                    "point_data": point_data,
                    "verification_status":True,
                    "is_active":True,
                }
            else:
                new_customer={
                    "name": incoming_data.get("name"),
                    "phone": query if is_phone_number(query) else '',
                    "id_card_number": query if is_id_card(query) else '',
                    "verification_status": False,
                    "is_active": True,
                }
                    
            return ApiResponse.success(
                message="Tạo khách hàng từ Auggest thành công",
                data=new_customer,
                status=status.HTTP_201_CREATED
            )