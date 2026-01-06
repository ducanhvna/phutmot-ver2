from django.urls import path
from . import views

urlpatterns = [
    # ví dụ: endpoint login
    path("base-price-raw/", views.BasePriceRawView.as_view(), name="base_price_raw/"),
]
