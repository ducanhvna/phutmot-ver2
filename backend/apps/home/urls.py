# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views
from .views import qr_scanned
from django.views.generic import TemplateView
from .views import decode_image

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('scan/', qr_scanned),  # Điện thoại gọi URL này khi quét QR
    path('scan_qr/', views.scan_qr_view, name='scan_qr'),  # View trang quét QR
    path('decode/', decode_image),
    path('pad/', TemplateView.as_view(template_name="products/pad.html")),  # Màn hình pad
    # Matches any html file
    #re_path(r'^.*\.*', views.pages, name='pages'),

]
