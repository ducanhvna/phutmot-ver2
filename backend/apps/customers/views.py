from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Customer
from .serializers import CustomerSerializer



from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

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
        qs = Customer.objects.filter(
            (
                Q(username__icontains=query) |
                Q(phone_number__icontains=query) |
                Q(id_card_number__icontains=query) |
                Q(old_id_card_number__icontains=query) |
                Q(name__icontains=query) |
                Q(english_name__icontains=query)
            )
        )
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