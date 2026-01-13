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
    # TPBGenQRView,
    PaymentView,
    PaymentQRProxyView,
    OrderShellView,
    OderDepositView,
    PaymentStatusCheckView,
    OderServiceView,
    WarehouseExportView,
    PaymentConfirmView,
    OrderDeTailView,
    OrderPaymentStatusView,
    DepositPaymentStatusView,
    # ProductDiscountView,
    # ProductDiscountViewAugges,
    # ProductDiscountBestView,
    BasePriceRawView,
    GetOrderDetailView,
    DepositDetailView,
    ServicesProductView,
    DonHangHomNayView,
    AttachedProductsView,
    DonHangHomNayTracocView
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

    # TPB B2B GenQR (UAT)
    # path("api/tpb/gen-qr/", TPBGenQRView.as_view(), name="tpb_gen_qr"),

    # Xử lý thanh toán
    path("api/payment/", PaymentView.as_view(), name="process_payment"),

    # Tra cứu trạng thái chuyển khoản (dummy)
    path("api/payment/transfer-status/", PaymentStatusCheckView.as_view(), name="payment_transfer_status"),

    # Proxy tạo QR từ hệ thống nội bộ
    path("api/payment/qr-proxy/", PaymentQRProxyView.as_view(), name="payment_qr_proxy"),

    # Đẩy đơn sang hệ thống backend nội bộ
    path("order-shell/", OrderShellView.as_view(), name="create_order_shell"),

    # Tạo đơn đặt cọc từ JSON
    path("api/deposit-order/", OderDepositView.as_view(), name="create_deposit_order"),

    # Tạo đơn dịch vụ từ JSON
    path("api/service-order/", OderServiceView.as_view(), name="create_service_order"),

    # Xuất kho sau khi thanh toán
    path("api/warehouse-export/", WarehouseExportView.as_view(), name="warehouse_export"),

    # Xác nhận thanh toán sau QR
    path("api/payment/confirm/", PaymentConfirmView.as_view(), name="payment_confirm"),
    
    #Chi tiết đơn hàng
    path("api/order-detail/", OrderDeTailView.as_view(), name="order_detail"),

    # Kiểm tra trạng thái thanh toán
    path("api/order-payment-status/", OrderPaymentStatusView.as_view(), name="order_payment_status"),

    # Kiểm tra trạng thái thanh toán đặt cọc
    path("api/deposit-payment-status/", DepositPaymentStatusView.as_view(), name="deposit_payment_status"),

    # Lấy số tiền chiết khấu cho sản phẩm
    # path("api/product-discount/", ProductDiscountView.as_view(), name="product_discount"),

    # # Lấy chiết khấu từ Augges
    # path("api/product-discount-augges/", ProductDiscountViewAugges.as_view(), name="product_discount_augges"),

    # # Chọn chiết khấu tốt nhất (nội bộ vs Augges)
    # path("api/product-discount-best/", ProductDiscountBestView.as_view(), name="product_discount_best"),

    # Proxy giá gốc (trả nguyên dữ liệu từ dịch vụ downstream)
    path("api/base-price-raw/", BasePriceRawView.as_view(), name="base_price_raw"),

    path("api/sell-detail-view/", GetOrderDetailView.as_view(), name="sell_detail_view"),

    path("api/deposit-detail-view/", DepositDetailView.as_view(), name="deposit_detai_view"),

    path("api/services-product/", ServicesProductView.as_view(), name="services_product_view"),

    path("api/today-orders/", DonHangHomNayView.as_view(), name="don_hang_hom_nay_view"),

    path("api/attached-products/", AttachedProductsView.as_view(), name="attached_products_view"),

    path("api/today-deposit-orders/", DonHangHomNayTracocView.as_view(), name="don_hang_hom_nay_tracoc_view"),
]
