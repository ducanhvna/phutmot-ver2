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

EXTERNAL_CUSTOMER_POINTS = f"{settings.EXTERNAL_CUSTOMER_POINTS}"
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
                    payload = {"tungay": 220917,
                                "denngay": 291014,
                                "sdt": query}
                    
                    # response = requests.post(EXTERNAL_CUSTOMER_POINTS, headers=headers, data=json.dumps(payload), timeout=25)
                    # point_data = response.json()
                    point_data = {
                        "status": 1,
                        "msg": "Successfully",
                        "data": 1635.0,
                        "diem224": 1285.0,
                        "diem225": 350.0,
                        "dauky": 0.0,
                        "diem226": 0.0,
                        "diem227": 0.0
                    }

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

class CustomerCreateView(PostOnlyAPIView):
    @staticmethod
    def create_customer_from_odoo(data):
        incoming_data = data
        
        # Validate required fields
        name = incoming_data.get("name", '').strip()
        phone = incoming_data.get("phone", '').strip()
        
        if not name:
            raise ValueError("Tên khách hàng là bắt buộc")
        
        if not phone or not is_phone_number(phone):
            raise ValueError("Số điện thoại hợp lệ là bắt buộc")
        
        # Prepare data for external API
        customer_payload = {
            'cccd_cmt': incoming_data.get('id_card_number', ''),
            'ho_ten_khach_hang': name,
            'gioi_tinh': 'nam' if incoming_data.get('gender') == 'Male' else ('nu' if incoming_data.get('gender') == 'Female' else 'khac'),
            'dia_chi': incoming_data.get('address', {}).get('dia_chi', ''),
            'ngay_sinh': incoming_data.get('birth_date', ''),
            'email': incoming_data.get('email', ''),
            'tinh': incoming_data.get('address', {}).get('tinh', ''),
            'quan': incoming_data.get('address', {}).get('quan', ''),
            'phuong': incoming_data.get('address', {}).get('phuong', ''),
            'nguoi_tao': incoming_data.get('nguoi_tao', ''),
            'dien_thoai': phone,
            'dien_thoai_2': incoming_data.get('dien_thoai_2', ''),
            'dien_thoai_3': incoming_data.get('dien_thoai_3', ''),
            'dien_thoai_4': incoming_data.get('dien_thoai_4', ''),
            'qr_code': incoming_data.get('qr_code', 1),
            'loai_nhan_vien': incoming_data.get('loai_nhan_vien', 0),
        }
        
        try:
            # Create customer in external system
            create_response = requests.post(EXTERNAL_CUSTOMER_ADD_URL, headers=headers, data=json.dumps(customer_payload), timeout=25)
            
            if create_response.status_code == 200:
                create_data = create_response.json()
                
                # Format response data
                new_customer = {
                    "id": create_data.get("id"),
                    "username": phone,
                    "name": name,
                    "phone": phone,
                    "id_card_number": incoming_data.get('id_card_number', ''),
                    "gender": incoming_data.get('gender', ''),
                    "birth_date": incoming_data.get('birth_date', ''),
                    "email": incoming_data.get('email', ''),
                    "address": incoming_data.get('address', {}),
                    "verification_status": True,
                    "is_active": True,
                }
                
                return new_customer
            else:
                raise ValueError(f"Lỗi tạo khách hàng: HTTP {create_response.status_code}")
                
        except requests.exceptions.Timeout:
            raise ValueError("Timeout khi kết nối đến augges")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Lỗi kết nối đến augges: {str(e)}")
        except Exception as e:
            raise ValueError(f"Lỗi không xác định: {str(e)}")

    def post(self, request):
        incoming_data = request.data
        
        try:
            new_customer = self.create_customer_from_odoo(incoming_data)
            return ApiResponse.success(
                message="Tạo khách hàng thành công",
                data=new_customer,
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return ApiResponse.error(
                message=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )