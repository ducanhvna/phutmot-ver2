from django.urls import path
from .views import (
    RateView,
)
urlpatterns = [
    # Lấy tỷ giá sản phẩm   
    path("rates/", RateView.as_view(), name="get_rate"),
]