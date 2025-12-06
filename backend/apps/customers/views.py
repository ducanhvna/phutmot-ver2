import logging
import requests, json
from django.db.models import Q

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import MethodNotAllowed
import re
from .models import Customer
from .serializers import CustomerSerializer

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

EXTERNAL_CUSTOMER_ADD_URL = "http://192.168.0.223:8869/api/public/khach_hang/add"
EXTERNAL_CUSTOMER_UPDATE_URL = "http://192.168.0.223:8869/api/public/khach_hang/update"
EXTERNAL_CUSTOMER_SEARCH_URL = "http://192.168.0.223:8869/api/public/khach_hang/timkiem"


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

    def post(self, request):
        query = (request.data.get("q") or "").strip()

        if not query:
            qs = Customer.objects.all().order_by("-id")
        else:
            qs = Customer.objects.filter(
                Q(username__icontains=query)
                | Q(phone_number__icontains=query)
                | Q(id_card_number__icontains=query)
                | Q(name__icontains=query)
            ).order_by("-id")

        serializer = CustomerSerializer(qs, many=True)
        return Response(serializer.data)


class CustomerCreateView(PostOnlyAPIView):

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
                    Customer.objects.create(
                        name= data.get("name"),
                        phone_number= query if is_phone_number(query) else '',
                        id_card_number= query if is_id_card(query) else '',
                        verification_status=True,
                        is_active=True,
                    )
                    if is_phone_number(query):
                        data["phone_number"] = query
                        data["name"] = data.get("name")
                        data["username"] = query
                        data["id_card_number"] = None
                        response = requests.post(EXTERNAL_CUSTOMER_ADD_URL, headers=headers, data=json.dumps(payload), timeout=15)
                        if response.status_code != 200:
                            logger.warning("External customer add failed (%s): %s", response.status_code, response.text)

                        serializer = CustomerSerializer(data=data)
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    customers = Customer.objects.filter(
                        Q(phone_number=query) | Q(id_card_number=query)
                    )
                    item = results[0]
                    birth_date = item.get("ngay_sinh")
                    for customer in customers:
                        phone_match = item.get("dien_thoai") == customer.phone_number
                        id_match = item.get("cccd_cmt") == customer.id_card_number

                        # Điều kiện update
                        if (phone_match and id_match) or \
                        (phone_match and not customer.id_card_number) or \
                        (id_match and not customer.phone_number):

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
                    if len(customers)>0:
                        serializer = CustomerSerializer(customer)
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                    else:
                        # Không có customer hiện hữu -> tạo mới
                        new_customer = Customer.objects.create(
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
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
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
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CustomerDetailView(PostOnlyAPIView):

    def post(self, request):
        pk = request.data.get("id") or request.data.get("pk")
        if not pk:
            return Response({"detail": "Thiếu id khách hàng"}, status=status.HTTP_400_BAD_REQUEST)

        customer = Customer.objects.filter(pk=pk).first()
        if customer is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        phone_number = customer.phone_number

        if phone_number:
            payload = {"sdt": phone_number}
            try:
                response = requests.post(EXTERNAL_CUSTOMER_SEARCH_URL, headers=headers, data=json.dumps(payload), timeout=15)
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
                        customer.refresh_from_db()
            except requests.RequestException as exc:
                logger.warning("External customer search failed for retrieve pk=%s: %s", pk, exc)

        serializer = CustomerSerializer(customer)
        # partners = []
        # if phone_number:
        #     from .utils import search_partner_by_mobile
        #     partners = search_partner_by_mobile(phone_number)
        #     if len(partners) == 0:
        #         from .utils import create_partner
        #         create_partner(customer.name, phone_number)
        #         partners = search_partner_by_mobile(phone_number)
        return Response({"data": serializer.data})


class CustomerUpdateView(PostOnlyAPIView):

    def post(self, request):
        pk = request.data.get("id") or request.data.get("pk")
        if not pk:
            return Response({"detail": "Thiếu id khách hàng"}, status=status.HTTP_400_BAD_REQUEST)

        customer = Customer.objects.filter(pk=pk).first()
        if customer is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        incoming_data = _map_local_fields(request.data)
        address = _parse_address(incoming_data)
        payload = _map_external_payload(incoming_data, address)

        try:
            response = requests.post(EXTERNAL_CUSTOMER_UPDATE_URL, headers=headers, data=json.dumps(payload), timeout=15)
            if response.status_code != 200:
                logger.warning("External customer update failed (%s): %s", response.status_code, response.text)
        except requests.RequestException as exc:
            logger.warning("External customer update request error: %s", exc)

        serializer = CustomerSerializer(customer, data=incoming_data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CustomerDeleteView(PostOnlyAPIView):

    def post(self, request):
        pk = request.data.get("id") or request.data.get("pk")
        if not pk:
            return Response({"detail": "Thiếu id khách hàng"}, status=status.HTTP_400_BAD_REQUEST)

        customer = Customer.objects.filter(pk=pk).first()
        if customer is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        customer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)