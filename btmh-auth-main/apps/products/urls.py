from django.urls import path
from . import views

urlpatterns = [
    # ví dụ: endpoint login
    path("lot/", views.SerialRawView.as_view(), name="update_lot/"),
]
