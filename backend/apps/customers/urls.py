from django.urls import path
from .views import (
	CustomerSearchView,
	CustomerCreateView,
	CustomerDetailView,
	CustomerUpdateView,
	CustomerDeleteView,
    OrderDepositTodayView,
    OrderSaleTodayView
)

urlpatterns = [
	path("search/", CustomerSearchView.as_view(), name="customer_search"),
	path("create/", CustomerCreateView.as_view(), name="customer_create"),
	path("detail/", CustomerDetailView.as_view(), name="customer_detail"),
	path("update/", CustomerUpdateView.as_view(), name="customer_update"),
	path("delete/", CustomerDeleteView.as_view(), name="customer_delete"),
    path("today-deposits/", OrderDepositTodayView.as_view(), name="today_deposits"),
    path("today-sales/", OrderSaleTodayView.as_view(), name='today_sales')
]