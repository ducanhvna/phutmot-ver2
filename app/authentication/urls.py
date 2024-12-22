# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from .views import login_view, register_user
from django.contrib.auth.views import LogoutView
from .views import EmployeeListCreateAPIView, EmployeeDetailAPIView

urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('api/employees/', EmployeeListCreateAPIView.as_view(), name='employee_list_create'),
    path('api/employees/<int:employee_id>/', EmployeeDetailAPIView.as_view(), name='employee_detail'),
]
