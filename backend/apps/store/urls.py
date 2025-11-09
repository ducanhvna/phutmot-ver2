from django.urls import path
from .views import (
    OrderView,
    InventoryCheckView,
    PrintInvoiceView,
    AttendanceView
)

urlpatterns = [
    # Tạo đơn hàng
    path("api/order/", OrderView.as_view(), name="create_order"),

    # Kiểm tra tồn kho
    path("api/inventory/", InventoryCheckView.as_view(), name="check_inventory"),

    # In hóa đơn
    path("api/invoice/print/", PrintInvoiceView.as_view(), name="print_invoice"),

    # Ghi nhận điểm danh
    path("api/attendance/", AttendanceView.as_view(), name="attendance"),
]
