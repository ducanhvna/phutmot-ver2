import logging
import requests, json

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import MethodNotAllowed

from .models import Customer
from .serializers import CustomerSerializer

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

    return data


class CustomerSearchView(PostOnlyAPIView):

    def post(self, request):
        query = (request.data.get("q") or "").strip()
        if not query:
            return Response({"detail": "Missing search query."}, status=status.HTTP_400_BAD_REQUEST)

        payload = {"sdt": query}

        try:
            response = requests.post(EXTERNAL_CUSTOMER_SEARCH_URL, headers=headers, data=json.dumps(payload), timeout=15)
        except requests.RequestException as e:
            return Response({"detail": f"Error connecting to service: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)

        if response.status_code != 200:
            return Response({"detail": "External service error", "status_code": response.status_code}, status=status.HTTP_502_BAD_GATEWAY)

        try:
            data = response.json()
        except ValueError:
            return Response({"detail": "Invalid JSON from external service"}, status=status.HTTP_502_BAD_GATEWAY)

        results = data.get("data", [])
        qs = []

        for item in results:
            username = item.get("ma_khach_hang") or item.get("dien_thoai")
            customer, created = Customer.objects.update_or_create(
                username=username,
                defaults={
                    "name": item.get("ho_ten_khach_hang"),
                    "phone_number": item.get("dien_thoai"),
                    "id_card_number": item.get("cccd_cmt"),
                    "gender": "Male" if item.get("gioi_tinh") == "Nam" else "Female" if item.get("gioi_tinh") == "Nữ" else None,
                    "birth_date": item.get("ngay_sinh").split(" ")[0] if item.get("ngay_sinh") else None,
                    "email": item.get("email"),
                    "address": {
                        "dia_chi": item.get("dia_chi"),
                        "tinh": item.get("tinh"),
                        "quan": item.get("quan"),
                        "phuong": item.get("phuong"),
                    },
                    "info": {
                        "ghi_chu": item.get("ghi_chu"),
                        "so_diem": item.get("so_diem"),
                        "hang": item.get("hang"),
                        "image_khach_hang": item.get("image_khach_hang"),
                        "qr_code": item.get("qr_code"),
                    },
                    "verification_status": True,
                    "is_active": True,
                }
            )
            qs.append(customer)

        serializer = CustomerSerializer(qs, many=True)
        return Response(serializer.data)


class CustomerCreateView(PostOnlyAPIView):

    def post(self, request):
        incoming_data = request.data
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