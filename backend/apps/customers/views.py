import logging
import requests, json
import datetime
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import MethodNotAllowed
import re
from .models import Customer
from .serializers import CustomerSerializer
from apps.home.utils import ApiResponse   # <-- class chuẩn hóa response
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
from django.utils import timezone

INTERNAL_API_BASE = settings.INTERNAL_API_BASE

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

logger = logging.getLogger(__name__)

EXTERNAL_CUSTOMER_ADD_URL = f"{settings.INTERNAL_API_BASE}/api/public/khach_hang/add"
EXTERNAL_CUSTOMER_UPDATE_URL = f"{settings.INTERNAL_API_BASE}/api/public/khach_hang/update"
EXTERNAL_CUSTOMER_SEARCH_URL = f"{settings.INTERNAL_API_BASE}/api/public/khach_hang/timkiem"


def _normalize_gender_for_downstream(value: str) -> str:
    if value is None:
        return ""
    v = str(value).strip()
    if not v:
        return ""
    # Downstream docs show lowercase "nam"/"nữ" but other parts use "Nam"/"Nữ".
    v_lower = v.lower()
    if v_lower in {"nam", "nữ", "nu"}:
        return "nữ" if v_lower in {"nữ", "nu"} else "nam"
    return v


def _normalize_date_for_downstream(value: str) -> str:
    """Return YYYY-MM-DD or empty string."""
    if value is None:
        return ""
    v = str(value).strip()
    if not v:
        return ""

    # Already ISO?
    try:
        datetime.datetime.strptime(v, "%Y-%m-%d")
        return v
    except ValueError:
        pass

    # dd/mm/yyyy
    try:
        d = datetime.datetime.strptime(v, "%d/%m/%Y").date()
        return d.isoformat()
    except ValueError:
        return v


# ---------------------------------------------------------------
# POST-only APIViews (similar style to apps.store)
# ---------------------------------------------------------------

class PostOnlyAPIView(APIView):
    """APIViews that reject GET and only allow POST/OPTIONS."""

    http_method_names = ["post", "options"]

    def get(self, request, *args, **kwargs):  # pragma: no cover - explicit 405
        raise MethodNotAllowed("GET")


def _parse_address(incoming_data):
    address_raw = incoming_data.get("address") or {}
    if isinstance(address_raw, str):
        try:
            return json.loads(address_raw)
        except ValueError:
            return {}
    return address_raw


def _map_external_payload(incoming_data, address):
    return {
        "cccd_cmt": incoming_data.get("cccd_cmt", ""),
        "ho_ten_khach_hang": incoming_data.get("ho_ten_khach_hang", ""),
        "gioi_tinh": incoming_data.get("gioi_tinh", ""),
        "dia_chi": address.get("dia_chi", incoming_data.get("dia_chi", "")),
        "ngay_sinh": incoming_data.get("ngay_sinh", ""),
        "email": incoming_data.get("email", ""),
        "tinh": address.get("tinh", incoming_data.get("tinh", "")),
        "quan": address.get("quan", incoming_data.get("quan", "")),
        "phuong": address.get("phuong", incoming_data.get("phuong", "")),
        "nguoi_tao": incoming_data.get("nguoi_tao", ""),
        "dien_thoai": incoming_data.get("dien_thoai", ""),
        "dien_thoai_2": incoming_data.get("dien_thoai_2", ""),
        "dien_thoai_3": incoming_data.get("dien_thoai_3", ""),
        "dien_thoai_4": incoming_data.get("dien_thoai_4", ""),
        "qr_code": incoming_data.get("qr_code", 1),
        "loai_nhan_vien": incoming_data.get("loai_nhan_vien", 0),
    }


def _map_local_fields(incoming_data):
    data = incoming_data.copy()

    name = data.get("name") or data.get("ho_ten_khach_hang") or ""
    phone = data.get("phone_number") or data.get("dien_thoai")
    username = (
        data.get("username")
        or phone
        or data.get("cccd_cmt")
        or data.get("ma_khach_hang")
        or name
    )

    if phone:
        data["phone_number"] = phone
    if name:
        data["name"] = name
    if username:
        data["username"] = phone
    if not data.get("id_card_number") and data.get("cccd_cmt"):
        data["id_card_number"] = data.get("cccd_cmt")
    if data.get("id_card_number") is None:
        data["id_card_number"] = None

    return data


class CustomerSearchView(PostOnlyAPIView):
    """
    API tìm kiếm khách hàng nội bộ có phân trang.

    📌 Endpoint:
    POST /api/customer/search/

    📥 Request body ví dụ:
    {
        "q": "0987654321",
        "page": 1,
        "page_size": 10
    }

    📤 Response ví dụ (HTTP 200):
    {
        "success": true,
        "message": "Tìm kiếm khách hàng thành công",
        "data": [
            {
                "id": 1,
                "username": "0987654321",
                "name": "Nguyễn Văn A",
                "phone_number": "0987654321",
                "id_card_number": "012345678",
                "email": "vana@example.com"
            }
        ],
        "pagination": {
            "page": 1,
            "page_size": 10,
            "total_items": 25,
            "total_pages": 3
        }
    }
    """
    def post(self, request):
        query = (request.data.get("q") or "").strip()
        qs = Customer.objects.all().order_by("-id")
        if query:
            qs = qs.filter(
                Q(username__icontains=query)
                | Q(phone_number__icontains=query)
                | Q(id_card_number__icontains=query)
                | Q(name__icontains=query)
            )

        paginator = PageNumberPagination()
        paginator.page_size = int(request.data.get("page_size", 10))
        result_page = paginator.paginate_queryset(qs, request)

        serializer = CustomerSerializer(result_page, many=True)

        pagination_info = {
            "page": paginator.page.number,
            "page_size": paginator.page.paginator.per_page,
            "total_items": paginator.page.paginator.count,
            "total_pages": paginator.page.paginator.num_pages,
        }

        return ApiResponse.success(
            message="Tìm kiếm khách hàng thành công",
            data=serializer.data,
            pagination=pagination_info
        )
    

class CustomerCreateView(PostOnlyAPIView):
    """
    API tạo mới khách hàng.

    🔎 Logic xử lý:
    | Có Auggest? | Có nội bộ? | Loại dữ liệu (Phone/ID) | Hành động xử lý | Kết quả |
    |-------------|------------|--------------------------|-----------------|---------|
    | ❌ Không    | ❌ Không   | 📱 Số điện thoại         | Tạo mới khách hàng nội bộ, đồng bộ thêm sang Auggest | **Tạo mới khách trên cả DB cửa hàng và DB Auggest** |
    | ❌ Không    | ❌ Không   | 🪪 Căn cước              | Tạo mới khách hàng nội bộ, không gửi sang Auggest | **Tạo mới khách chỉ trên DB cửa hàng** |
    | ❌ Không    | ✅ Có      | 📱 Số điện thoại         | Cập nhật nội bộ nếu cần, đồng bộ thêm sang Auggest | **Giữ/cập nhật khách trên DB cửa hàng, tạo mới trên DB Auggest** |
    | ❌ Không    | ✅ Có      | 🪪 Căn cước              | Cập nhật nội bộ, không gửi sang Auggest | **Giữ/cập nhật khách chỉ trên DB cửa hàng** |
    | ✅ Có       | ❌ Không   | 📱 Số điện thoại         | Tạo mới khách hàng nội bộ từ dữ liệu Auggest | **Tạo mới khách chỉ trên DB cửa hàng (dữ liệu lấy từ Auggest)** |
    | ✅ Có       | ❌ Không   | 🪪 Căn cước              | Tạo mới khách hàng nội bộ từ dữ liệu Auggest | **Tạo mới khách chỉ trên DB cửa hàng (dữ liệu lấy từ Auggest)** |
    | ✅ Có       | ✅ Có      | 📱 Số điện thoại         | So khớp và cập nhật nội bộ theo dữ liệu Auggest | **Cập nhật khách trên DB cửa hàng, giữ nguyên trên DB Auggest** |
    | ✅ Có       | ✅ Có      | 🪪 Căn cước              | So khớp và cập nhật nội bộ theo dữ liệu Auggest | **Cập nhật khách trên DB cửa hàng, giữ nguyên trên DB Auggest** |

    ---

    📌 Endpoint:
    POST /api/customer/create/

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
            response = requests.post(EXTERNAL_CUSTOMER_SEARCH_URL, headers=headers, data=json.dumps(payload), timeout=15)
            if response.status_code == 200:
                data = response.json()
                results = data.get("data", [])

                if not results:
                    # Không tìm thấy -> tạo mới
                    new_customer, created = Customer.objects.update_or_create(
                        username=query,
                        defaults={
                            "name": incoming_data.get("name"),
                            "phone_number": query if is_phone_number(query) else '',
                            "id_card_number": query if is_id_card(query) else '',
                            "verification_status": True,
                            "is_active": True,
                        }
                    )

                    if is_phone_number(query):
                        data = {"phone_number": query, "name": incoming_data.get("name"), "username": query, "id_card_number": None}
                        response = requests.post(EXTERNAL_CUSTOMER_ADD_URL, headers=headers, data=json.dumps(payload), timeout=15)
                        if response.status_code != 200:
                            logger.warning("External customer add failed (%s): %s", response.status_code, response.text)

                    serializer = CustomerSerializer(new_customer)
                    return ApiResponse.success(
                        message="Tạo khách hàng thành công",
                        data=serializer.data,
                        status=status.HTTP_201_CREATED
                    )

                # Có kết quả từ Auggest -> cập nhật hoặc tạo mới
                customers = Customer.objects.filter(Q(phone_number=query) | Q(id_card_number=query))
                item = results[0]
                birth_date = item.get("ngay_sinh")

                for customer in customers:
                    phone_match = item.get("dien_thoai") == customer.phone_number
                    id_match = item.get("cccd_cmt") == customer.id_card_number

                    if (phone_match and id_match) or (phone_match and not customer.id_card_number) or (id_match and not customer.phone_number):
                        Customer.objects.filter(pk=customer.pk).update(
                            name=item.get("ho_ten_khach_hang") or customer.name,
                            phone_number=item.get("dien_thoai") or customer.phone_number,
                            id_card_number=item.get("cccd_cmt") or customer.id_card_number,
                            gender="Male" if item.get("gioi_tinh") == "Nam" else "Female" if item.get("gioi_tinh") == "Nữ" else customer.gender,
                            birth_date=birth_date.split(" ")[0] if birth_date else customer.birth_date,
                            email=item.get("email") or customer.email,
                            address={
                                "dia_chi": item.get("dia_chi"),
                                "tinh": item.get("tinh"),
                                "quan": item.get("quan"),
                                "phuong": item.get("phuong"),
                            },
                            info={
                                "ghi_chu": item.get("ghi_chu"),
                                "so_diem": item.get("so_diem"),
                                "hang": item.get("hang"),
                                "image_khach_hang": item.get("image_khach_hang"),
                                "qr_code": item.get("qr_code"),
                            },
                            verification_status=True,
                            is_active=True,
                        )

                if customers.exists():
                    serializer = CustomerSerializer(customers.first())
                    return ApiResponse.success(
                        message="Cập nhật khách hàng thành công",
                        data=serializer.data,
                        status=status.HTTP_201_CREATED
                    )
                else:
                    # Không có customer hiện hữu -> tạo mới từ dữ liệu Auggest
                    new_customer = Customer.objects.create(
                        username=item.get("dien_thoai"),
                        name=item.get("ho_ten_khach_hang") or "",
                        phone_number=item.get("dien_thoai") or "",
                        id_card_number=item.get("cccd_cmt") or "",
                        gender="Male" if item.get("gioi_tinh") == "Nam" else "Female" if item.get("gioi_tinh") == "Nữ" else "",
                        birth_date=birth_date.split(" ")[0] if birth_date else None,
                        email=item.get("email") or "",
                        address={
                            "dia_chi": item.get("dia_chi"),
                            "tinh": item.get("tinh"),
                            "quan": item.get("quan"),
                            "phuong": item.get("phuong"),
                        },
                        info={
                            "ghi_chu": item.get("ghi_chu"),
                            "so_diem": item.get("so_diem"),
                            "hang": item.get("hang"),
                            "image_khach_hang": item.get("image_khach_hang"),
                            "qr_code": item.get("qr_code"),
                        },
                        verification_status=True,
                        is_active=True,
                    )
                    serializer = CustomerSerializer(new_customer)
                    return ApiResponse.success(
                        message="Tạo khách hàng từ Auggest thành công",
                        data=serializer.data,
                        status=status.HTTP_201_CREATED
                    )

        # Trường hợp không phải phone/ID -> tạo mới nội bộ
        data = _map_local_fields(incoming_data)
        address = _parse_address(incoming_data)
        payload = _map_external_payload(incoming_data, address)

        try:
            response = requests.post(EXTERNAL_CUSTOMER_ADD_URL, headers=headers, data=json.dumps(payload), timeout=15)
            if response.status_code != 200:
                logger.warning("External customer add failed (%s): %s", response.status_code, response.text)
        except requests.RequestException as exc:
            logger.warning("External customer add request error: %s", exc)

        serializer = CustomerSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ApiResponse.success(
            message="Tạo khách hàng nội bộ thành công",
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )


class CustomerEIDSyncView(PostOnlyAPIView):
    """Đồng bộ/Update khách hàng bằng payload EID.

    Luồng theo yêu cầu:
    - Nhận payload EID (fullName..dsCert) + sdt/phone.
    - Gọi downstream search (timkiem) theo sdt.
    - Nếu downstream trả về CCCD và KHỚP => cho update.
    - Nếu downstream trả về CCCD và KHÔNG KHỚP => fail.
    - Nếu downstream không có CCCD => cho update.

    Endpoint:
    POST /api/customers/eid-sync/
    """

    def post(self, request):
        incoming = request.data or {}

        phone = (incoming.get("sdt") or incoming.get("phone") or incoming.get("dien_thoai") or "").strip()
        if not phone:
            return ApiResponse.error(message="Thiếu tham số sdt/phone", status=status.HTTP_400_BAD_REQUEST)

        input_cccd = (incoming.get("cccd_cmt") or incoming.get("identityNumber") or incoming.get("id_card_number") or "").strip()
        if not input_cccd:
            return ApiResponse.error(message="Thiếu CCCD/identityNumber (cccd_cmt)", status=status.HTTP_400_BAD_REQUEST)

        # --- 1) Search downstream by sdt ---
        try:
            search_resp = requests.post(
                EXTERNAL_CUSTOMER_SEARCH_URL,
                headers=headers,
                data=json.dumps({"sdt": phone}),
                timeout=15,
            )
        except requests.RequestException as exc:
            return ApiResponse.error(
                message="Không gọi được API tìm kiếm khách hàng (downstream)",
                data={"error": str(exc)},
                status=502,
            )

        if search_resp.status_code != 200:
            return ApiResponse.error(
                message="Downstream tìm kiếm khách hàng thất bại",
                data={"status_code": search_resp.status_code, "body": search_resp.text},
                status=502,
            )

        try:
            search_json = search_resp.json()
        except ValueError:
            return ApiResponse.error(
                message="Downstream tìm kiếm trả về dữ liệu không hợp lệ",
                data={"body": search_resp.text},
                status=502,
            )

        candidates = search_json.get("data") or []
        if not candidates:
            return ApiResponse.error(
                message="Không tìm thấy khách hàng theo sdt trên downstream",
                data={"sdt": phone},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Prefer exact phone match if list contains multiple
        selected = None
        for item in candidates:
            if str(item.get("dien_thoai") or "").strip() == phone:
                selected = item
                break
        if selected is None:
            selected = candidates[0]

        downstream_cccd = (selected.get("cccd_cmt") or "").strip()
        if downstream_cccd and downstream_cccd != input_cccd:
            return ApiResponse.error(
                message="CCCD không khớp với khách hàng đã tồn tại trên downstream",
                data={"sdt": phone, "downstream_cccd": downstream_cccd, "input_cccd": input_cccd},
                status=409,
            )

        cccd_to_set = downstream_cccd or input_cccd

        # --- 2) Build downstream update payload ---
        full_name = (incoming.get("fullName") or incoming.get("ho_ten_khach_hang") or incoming.get("name") or selected.get("ho_ten_khach_hang") or "").strip()
        gender = _normalize_gender_for_downstream(incoming.get("sex") or incoming.get("gioi_tinh") or selected.get("gioi_tinh"))
        dob = _normalize_date_for_downstream(incoming.get("dateOfBirth") or incoming.get("ngay_sinh") or selected.get("ngay_sinh"))
        email = (incoming.get("email") or selected.get("email") or "").strip()

        # Prefer placeOfResidence from EID payload, fall back to dia_chi
        dia_chi = (
            incoming.get("placeOfResidence")
            or incoming.get("dia_chi")
            or selected.get("dia_chi")
            or ""
        )
        dia_chi = str(dia_chi).strip()

        update_payload = {
            "cccd_cmt": cccd_to_set,
            "ho_ten_khach_hang": full_name,
            "gioi_tinh": gender,
            "dia_chi": dia_chi,
            "ngay_sinh": dob,
            "email": email,
            "tinh": (incoming.get("tinh") or selected.get("tinh") or ""),
            "quan": (incoming.get("quan") or selected.get("quan") or ""),
            "phuong": (incoming.get("phuong") or selected.get("phuong") or ""),
            "nguoi_tao": (incoming.get("nguoi_tao") or ""),
            "dien_thoai": phone,
            # downstream search sometimes returns dien_thoai2/3/4, while update expects dien_thoai_2/3/4
            "dien_thoai_2": (incoming.get("dien_thoai_2") or incoming.get("dien_thoai2") or selected.get("dien_thoai2") or selected.get("dien_thoai_2") or ""),
            "dien_thoai_3": (incoming.get("dien_thoai_3") or incoming.get("dien_thoai3") or selected.get("dien_thoai3") or selected.get("dien_thoai_3") or ""),
            "dien_thoai_4": (incoming.get("dien_thoai_4") or incoming.get("dien_thoai4") or selected.get("dien_thoai4") or selected.get("dien_thoai_4") or ""),
            "qr_code": incoming.get("qr_code", selected.get("qr_code", 1)),
            "loai_nhan_vien": incoming.get("loai_nhan_vien", 0),
        }

        # --- 3) Call downstream update ---
        try:
            update_resp = requests.post(
                EXTERNAL_CUSTOMER_UPDATE_URL,
                headers=headers,
                data=json.dumps(update_payload),
                timeout=15,
            )
        except requests.RequestException as exc:
            return ApiResponse.error(
                message="Không gọi được API update khách hàng (downstream)",
                data={"error": str(exc)},
                status=502,
            )

        downstream_update_payload = {"status_code": update_resp.status_code}
        try:
            downstream_update_payload["json"] = update_resp.json()
        except ValueError:
            downstream_update_payload["text"] = update_resp.text

        if update_resp.status_code != 200:
            return ApiResponse.error(
                message="Downstream update khách hàng thất bại",
                data=downstream_update_payload,
                status=502,
            )

        # Some implementations return {status: 1, msg: Successfully}
        downstream_status = None
        if isinstance(downstream_update_payload.get("json"), dict):
            downstream_status = downstream_update_payload["json"].get("status")
        if downstream_status not in (None, 1, 200):
            return ApiResponse.error(
                message="Downstream update trả về trạng thái không thành công",
                data=downstream_update_payload,
                status=502,
            )

        # --- 4) Update local customer (store DB) + lưu EID raw payload ---
        eid_raw = {
            "fullName": incoming.get("fullName"),
            "dateOfBirth": incoming.get("dateOfBirth"),
            "sex": incoming.get("sex"),
            "nationality": incoming.get("nationality"),
            "placeOfOrigin": incoming.get("placeOfOrigin"),
            "placeOfResidence": incoming.get("placeOfResidence"),
            "personalIdentification": incoming.get("personalIdentification"),
            "identityNumber": input_cccd,
            "facePhoto": incoming.get("facePhoto"),
            "com": incoming.get("com"),
            "sod": incoming.get("sod"),
            "dg1": incoming.get("dg1"),
            "dg2": incoming.get("dg2"),
            "dg13": incoming.get("dg13"),
            "dg14": incoming.get("dg14"),
            "dg15": incoming.get("dg15"),
            "dsCert": incoming.get("dsCert"),
        }
        # drop None keys to avoid bloating
        eid_raw = {k: v for k, v in eid_raw.items() if v is not None}

        customer, _created = Customer.objects.update_or_create(
            username=phone,
            defaults={
                "name": full_name or phone,
                "phone_number": phone,
                "id_card_number": cccd_to_set,
                "verification_status": True,
                "is_active": True,
                "email": email or None,
                "address": {
                    "dia_chi": dia_chi,
                    "tinh": update_payload.get("tinh") or "",
                    "quan": update_payload.get("quan") or "",
                    "phuong": update_payload.get("phuong") or "",
                },
            },
        )

        info = customer.info if isinstance(customer.info, dict) else {}
        info["eid"] = {
            "synced_at": timezone.now().isoformat(),
            "payload": eid_raw,
        }
        customer.info = info
        customer.touch_store_activity()

        serializer = CustomerSerializer(customer)
        return ApiResponse.success(
            message="Đồng bộ EID và cập nhật khách hàng thành công",
            data={
                "customer": serializer.data,
                "downstream": {
                    "search": {"count": len(candidates), "selected": selected},
                    "update": downstream_update_payload,
                },
            },
            status=status.HTTP_200_OK,
        )



class CustomerDetailView(PostOnlyAPIView):
    """
    API lấy chi tiết khách hàng theo id/pk.

    📌 Endpoint:
    POST /api/customer/detail/

    📥 Request body ví dụ:
    {
        "id": 1
    }

    📤 Response ví dụ (HTTP 200):
    {
        "success": true,
        "message": "Lấy chi tiết khách hàng thành công",
        "data": {
            "id": 1,
            "username": "0987654321",
            "name": "Nguyễn Văn A",
            "phone_number": "0987654321",
            "id_card_number": "012345678",
            "email": "vana@example.com"
        }
    }

    📤 Response ví dụ (HTTP 400 - thiếu id):
    {
        "success": false,
        "message": "Thiếu id khách hàng",
        "data": []
    }

    📤 Response ví dụ (HTTP 404 - không tìm thấy):
    {
        "success": false,
        "message": "Không tìm thấy khách hàng",
        "data": []
    }
    """

    def post(self, request):
        pk = request.data.get("id") or request.data.get("pk")
        if not pk:
            return ApiResponse.error(
                message="Thiếu id khách hàng",
                status=status.HTTP_400_BAD_REQUEST
            )

        customer = Customer.objects.filter(pk=pk).first()
        if customer is None:
            return ApiResponse.error(
                message="Không tìm thấy khách hàng",
                status=status.HTTP_404_NOT_FOUND
            )

        phone_number = customer.phone_number

        if phone_number:
            payload = {"sdt": phone_number}
            try:
                response = requests.post(
                    EXTERNAL_CUSTOMER_SEARCH_URL,
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=15
                )
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("data", [])
                    if results:
                        item = results[0]
                        birth_date = item.get("ngay_sinh")
                        Customer.objects.filter(pk=customer.pk).update(
                            name=item.get("ho_ten_khach_hang") or customer.name,
                            phone_number=item.get("dien_thoai") or customer.phone_number,
                            id_card_number=item.get("cccd_cmt") or customer.id_card_number,
                            gender="Male" if item.get("gioi_tinh") == "Nam"
                                   else "Female" if item.get("gioi_tinh") == "Nữ"
                                   else customer.gender,
                            birth_date=birth_date.split(" ")[0] if birth_date else customer.birth_date,
                            email=item.get("email") or customer.email,
                            address={
                                "dia_chi": item.get("dia_chi"),
                                "tinh": item.get("tinh"),
                                "quan": item.get("quan"),
                                "phuong": item.get("phuong"),
                            },
                            info={
                                "ghi_chu": item.get("ghi_chu"),
                                "so_diem": item.get("so_diem"),
                                "hang": item.get("hang"),
                                "image_khach_hang": item.get("image_khach_hang"),
                                "qr_code": item.get("qr_code"),
                            },
                            verification_status=True,
                            is_active=True,
                        )
                        customer.refresh_from_db()
            except requests.RequestException as exc:
                logger.warning("External customer search failed for retrieve pk=%s: %s", pk, exc)

        serializer = CustomerSerializer(customer)
        return ApiResponse.success(
            message="Lấy chi tiết khách hàng thành công",
            data=serializer.data
        )



class CustomerUpdateView(PostOnlyAPIView):
    """
    API cập nhật thông tin khách hàng.

    📌 Endpoint:
    POST /api/customer/update/

    📥 Request body ví dụ:
    {
        "id": 1,
        "name": "Nguyễn Văn A (updated)",
        "email": "vana_new@example.com"
    }

    📤 Response ví dụ (HTTP 200):
    {
        "success": true,
        "message": "Cập nhật khách hàng thành công",
        "data": {
            "id": 1,
            "username": "0987654321",
            "name": "Nguyễn Văn A (updated)",
            "phone_number": "0987654321",
            "id_card_number": "012345678",
            "email": "vana_new@example.com"
        }
    }
    """
    def post(self, request):
        pk = request.data.get("id") or request.data.get("pk")
        if not pk:
            return ApiResponse.error(
                message="Thiếu id khách hàng",
                status=status.HTTP_400_BAD_REQUEST
            )

        customer = Customer.objects.filter(pk=pk).first()
        if customer is None:
            return ApiResponse.error(
                message="Không tìm thấy khách hàng",
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CustomerSerializer(customer, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return ApiResponse.success(
            message="Cập nhật khách hàng thành công",
            data=serializer.data
        )


class CustomerDeleteView(PostOnlyAPIView):
    """
    API xóa khách hàng theo id/pk.

    📌 Endpoint:
    POST /api/customer/delete/

    📥 Request body ví dụ:
    {
        "id": 1
    }

    📤 Response ví dụ (HTTP 204):
    {
        "success": true,
        "message": "Xóa khách hàng thành công",
        "data": []
    }
    """

    def post(self, request):
        pk = request.data.get("id") or request.data.get("pk")
        if not pk:
            return ApiResponse.error(
                message="Thiếu id khách hàng",
                status=status.HTTP_400_BAD_REQUEST
            )

        customer = Customer.objects.filter(pk=pk).first()
        if customer is None:
            return ApiResponse.error(
                message="Không tìm thấy khách hàng",
                status=status.HTTP_404_NOT_FOUND
            )

        customer.delete()
        return ApiResponse.success(
            message="Xóa khách hàng thành công",
            data=[],
            status=status.HTTP_204_NO_CONTENT
        )


class OrderDepositTodayView(APIView):
    """
    API lấy danh sách đặt cọc của khách hàng trong ngày hôm nay (theo múi giờ Việt Nam).

    📌 Endpoint:
    GET /api/order/deposit/today/?phone=0979410826

    📥 Request params:
    - phone: số điện thoại khách hàng

    📤 Response ví dụ (HTTP 200):
    {
        "success": true,
        "message": "Lấy danh sách đặt cọc hôm nay thành công",
        "data": {
            "date": "2025-12-10",
            "downstream": { ... }   # dữ liệu từ API nội bộ
        }
    }
    """
    base_url = f"{INTERNAL_API_BASE}/api/public/don_hang_dat_coc_ngay"
    headers = {"Content-Type": "application/json; charset=utf-8"}

    def get(self, request):
        phone = request.query_params.get("phone")
        if not phone:
            return ApiResponse.error(
                message="Thiếu tham số phone",
                status=400
            )

        # Lấy ngày hôm nay theo múi giờ Việt Nam (dựa vào TIME_ZONE trong settings.py)
        vn_now = timezone.localtime(timezone.now())
        today_str = vn_now.strftime("%Y-%m-%d")

        url = f"{self.base_url}/{phone}/{today_str}"
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            downstream = response.json() if response.ok else {"raw": response.text}

            if response.ok:
                return ApiResponse.success(
                    message="Lấy danh sách đặt cọc hôm nay thành công",
                    data={"date": today_str, "downstream": downstream},
                    status=response.status_code
                )
            else:
                return ApiResponse.error(
                    message="Không lấy được danh sách đặt cọc hôm nay",
                    data={"date": today_str, "downstream": downstream},
                    status=response.status_code
                )
        except requests.RequestException as exc:
            return ApiResponse.error(
                message="Không gọi được dịch vụ danh sách đặt cọc",
                data={"error": str(exc), "date": today_str},
                status=502
            )

class OrderSaleTodayView(APIView):
    """
    API lấy danh sách đơn hàng bán của khách hàng trong ngày hôm nay (theo múi giờ Việt Nam).

    📌 Endpoint:
    GET /api/order/sale/today/?phone=0979259516

    📥 Request params:
    - phone: số điện thoại khách hàng

    📤 Response ví dụ (HTTP 200):
    {
        "success": true,
        "message": "Lấy danh sách đơn hàng bán hôm nay thành công",
        "data": {
            "date": "2025-12-10",
            "downstream": { ... }   # dữ liệu từ API nội bộ
        }
    }
    """
    base_url = f"{INTERNAL_API_BASE}/api/public/don_hang_ngay"
    headers = {"Content-Type": "application/json; charset=utf-8"}

    def get(self, request):
        phone = request.query_params.get("phone")
        if not phone:
            return ApiResponse.error(
                message="Thiếu tham số phone",
                status=400
            )

        # Lấy ngày hôm nay theo múi giờ Việt Nam (dựa vào TIME_ZONE trong settings.py)
        vn_now = timezone.localtime(timezone.now())
        today_str = vn_now.strftime("%Y-%m-%d")

        url = f"{self.base_url}/{phone}/{today_str}"
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            downstream = response.json() if response.ok else {"raw": response.text}

            if response.ok:
                return ApiResponse.success(
                    message="Lấy danh sách đơn hàng bán hôm nay thành công",
                    data={"date": today_str, "downstream": downstream},
                    status=response.status_code
                )
            else:
                return ApiResponse.error(
                    message="Không lấy được danh sách đơn hàng bán hôm nay",
                    data={"date": today_str, "downstream": downstream},
                    status=response.status_code
                )
        except requests.RequestException as exc:
            return ApiResponse.error(
                message="Không gọi được dịch vụ danh sách đơn hàng bán",
                data={"error": str(exc), "date": today_str},
                status=502
            )

