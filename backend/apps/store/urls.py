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
    PaymentView,
    OrderSellView,
    OderPurchaseView,
    OderDepositView,
    ProductImageView,
    OrderReplaceView,
    OderServiceView
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

    # Tạo đơn bán hàng từ JSON
    path("api/order-sell/", OrderSellView.as_view(), name="create_order_sell"),

    # Tạo đơn mua hàng từ JSON
    path("api/order-purchase/", OderPurchaseView.as_view(), name="create_order_purchase"),

    # Tạo đơn đặt cọc từ JSON
    path("api/deposit-order/", OderDepositView.as_view(), name="create_deposit_order"),

    # Tạo đơn dịch vụ từ JSON
    path("api/service-order/", OderServiceView.as_view(), name="create_service_order"),
    
    # Tạo đơn đổi hàng JSON
    path("api/replace-order/", OrderReplaceView.as_view(), name="create_replace_order") 
]
