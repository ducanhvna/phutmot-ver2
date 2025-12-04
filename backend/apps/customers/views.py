from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Customer
from .serializers import CustomerSerializer
import requests, json
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

# Header
headers = {
    "Content-Type": "application/json; charset=utf-8"
}
class CustomerPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    pagination_class = CustomerPagination

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({'detail': 'Missing search query.'}, status=status.HTTP_400_BAD_REQUEST)
        # Ghép payload
        payload = {
            "sdt": query # số điện thoại hoặc căn cước
        }
        search_url = "http://192.168.0.223:8869/api/public/khach_hang/timkiem"

        print(payload)
        # Gọi API POST
        response = requests.post(search_url, headers=headers, data=json.dumps(payload))

        # In kết quả
        print("Status code:", response.status_code)
        print("Response body:", response.text)

        
        try:
            response = requests.post(search_url, headers=headers, data=json.dumps(payload))
        except requests.RequestException as e:
            return Response({'detail': f'Error connecting to service: {str(e)}'}, status=status.HTTP_502_BAD_GATEWAY)

        if response.status_code != 200:
            return Response({'detail': 'External service error', 'status_code': response.status_code}, status=status.HTTP_502_BAD_GATEWAY)

        try:
            data = response.json()
        except ValueError:
            return Response({'detail': 'Invalid JSON from external service'}, status=status.HTTP_502_BAD_GATEWAY)

        results = data.get("data", [])
        qs = []

        for item in results:
            # Map dữ liệu từ service sang Customer
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
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        customer = queryset.filter(pk=pk).first()
        if customer is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(customer)
        phone_number = customer.phone_number
        partners = []
        if phone_number:
            from .utils import search_partner_by_mobile
            partners = search_partner_by_mobile(phone_number)
            if len(partners) == 0:
                from .utils import create_partner
                create_partner(customer.name, phone_number)
                partners = search_partner_by_mobile(phone_number)
        return Response({"data": serializer.data, "partners": partners})

    def update(self, request, pk=None):
        customer = self.get_object()
        serializer = self.get_serializer(customer, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        customer = self.get_object()
        self.perform_destroy(customer)
        return Response(status=status.HTTP_204_NO_CONTENT)