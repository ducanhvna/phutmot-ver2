from django.urls import path
from .views import (
    RateView,
    RateUpdateView
)
urlpatterns = [
    # Lấy tỷ giá sản phẩm   
    path("rates/", RateView.as_view(), name="get_rate"),
    path("rates/update/", RateUpdateView.as_view(), name="update_rate"),
]