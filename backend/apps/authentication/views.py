# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
import jwt
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .forms import LoginForm, SignUpForm
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

import jwt
from datetime import datetime, timedelta
from django.http import JsonResponse

# Load private key
with open("private.pem", "r") as f:
    PRIVATE_KEY = f.read()

def login_view(request):
    username = request.POST.get("username")
    password = request.POST.get("password")
    user = authenticate(username=username, password=password)
    # Giả sử xác thực thành công
    if user:
        payload = {
            "sub": username,
            "exp": datetime.utcnow() + timedelta(hours=12),
            "iat": datetime.utcnow(),
        }
        token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")
        return JsonResponse({"access_token": token})
    return JsonResponse({"error": "Invalid credentials"}, status=401)

def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg = 'User created - please <a href="/login">login</a>.'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})

from apps.home.utils import ApiResponse

class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            payload = {
                "sub": user.username,
                "username": user.username,
                "role": "sales",
                "exp": datetime.utcnow() + timedelta(days=10),
                "iat": datetime.utcnow(),
                "iss": "sales-app",
            }
            token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")
            return ApiResponse.success(
                message="Đăng nhập thành công",
                data= {
                    "store_token": token,
                    "access": str(refresh.access_token),
                    "printers": ['tichtru', 'tho', 'trangsuc'],
                    "store_url": 'https://solienlacdientu.info' if 'a' in user.username else 'http://192.168.10.26',
                    "refresh": str(refresh),
                }
            )
        return ApiResponse.error(message="Sai tài khoản hoặc mật khẩu", status=401)



class StoreRefreshTokenView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        brand = request.data.get("brand")
        if not brand:
            return ApiResponse.error(message="Thiếu tham số 'brand'", status=400)

        if not user.is_superuser:
            return ApiResponse.error(message="Không có quyền. Cần superuser.", status=403)

        refresh = RefreshToken.for_user(user)
        payload = {
            "sub": brand,
            "username": user.username,
            "role": "store-admin",
            "exp": datetime.utcnow() + timedelta(days=9999),
            "iat": datetime.utcnow(),
            "iss": "store-app",
        }
        store_token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")

        return ApiResponse.success(
            message="Tạo store token thành công",
            data={
                "store_token": store_token,
                "refresh": str(refresh),
            }
        )
