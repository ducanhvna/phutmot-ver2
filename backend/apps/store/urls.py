from django.urls import path
from .views import (
    OrderView,
    InventoryCheckView,
    PrintInvoiceView,
    AttendanceView,
    RateView,
    AllRateView,
    PriceCalcView,
    GenQRView,
    PaymentView
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

    # Lấy tỷ giá sản phẩm
    path("api/rate/", RateView.as_view(), name="get_rate"),

    # Lấy tất cả tỷ giá
    path("api/rates/", AllRateView.as_view(), name="get_all_rates"),

    # Tính giá sản phẩm
    path("api/price-calc/", PriceCalcView.as_view(), name="price_calc"),

    # Tạo mã QR
    path("api/generate-qr/", GenQRView.as_view(), name="generate_qr"),

    # Xử lý thanh toán
    path("api/payment/", PaymentView.as_view(), name="process_payment"),
]
