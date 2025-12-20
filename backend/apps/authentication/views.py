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
from django.conf import settings
import jwt
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.contrib.auth import get_user_model

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
    """
    API: Đăng nhập hệ thống

    Endpoint:
    POST /api/login/

    Mô tả:
    API dùng để xác thực người dùng bằng username và password. 
    Nếu đăng nhập thành công, hệ thống trả về token JWT cùng thông tin liên quan.

    Request:
    - Method: POST
    - Headers:
    Content-Type: application/json
    - Body:
    {
    "username": "admin",
    "password": "your_password"
    }

    Response:

    1. Thành công (HTTP 200):
    {
    "success": true,
    "message": "Đăng nhập thành công",
    "data": {
        "store_token": "<JWT RS256 token>",
        "access": "<JWT access token>",
        "printers": [
        "tichtru",
        "tho",
        "trangsuc"
        ],
        "store_url": "https://solienlacdientu.info",
        "refresh": "<JWT refresh token>"
    }
    }

    2. Thất bại (HTTP 401):
    {
    "success": false,
    "message": "Sai tài khoản hoặc mật khẩu",
    "data": []
    }

    Các trường dữ liệu trả về:
    - success (boolean): Trạng thái thành công hay thất bại
    - message (string): Thông điệp mô tả kết quả đăng nhập
    - data (object): Dữ liệu trả về khi đăng nhập thành công
    - store_token (string): JWT token riêng cho store (ký bằng RSA private key)
    - access (string): Access token (JWT) dùng cho các API yêu cầu xác thực
    - printers (array): Danh sách máy in được gán cho user/store
    - store_url (string): URL cửa hàng
    - refresh (string): Refresh token (JWT) để lấy access token mới khi hết hạn
    """
    def post(self, request):
        import xmlrpc.client
        username = request.data.get("username")
        password = request.data.get("password")
        # Thử xác thưc người dùng trên odoo nếu thành công thì tạo user cục bộ
        uid = None
        company_id = None
        company_store_website = None
        ex = ""
        try:
            ODOO_URL = settings.ODDO_SERVER_URL
            ODOO_DB =  settings.ODDO_DB
            ROOT_ODOO_USER = settings.ODDO_USERNAME
            ROOT_ODOO_PASS = settings.ODDO_PASSWORD
            # 1. Authenticate
            common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
            uid = common.authenticate(ODOO_DB, username, password, {})
            if not uid:
                # Tim kiem username trong odoo khong thay thi tra ve loi uid
                model = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
                user_ids = model.execute_kw(ODOO_DB, settings.ODDO_ADMIN_UID, ROOT_ODOO_PASS,
                    'res.users', 'search',
                    [['|', ['login', '=', username], ['email', '=', username]]])
                if not user_ids:
                    uid = user_ids[0]
                # return {'status': 'fail', 'msg': 'Odoo login failed'}
            else:
                # find or create local user
                User = get_user_model()
                user, created = User.objects.get_or_create(username=username)
                if created:
                    user.set_password(password)
                    user.save()

            # Ở đây bạn có thể lấy thêm thông tin công ty nếu cần
            # Tạo models proxy để gọi các method
            models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

            company_id = models.execute_kw(
                ODOO_DB, settings.ODDO_ADMIN_UID, ROOT_ODOO_PASS,
                'res.users', 'read',
                [uid],
                {'fields': ['company_id']}
            )[0]['company_id'][0]

            company_store_website = model.execute_kw(ODOO_DB, uid, password,
                'res.company', 'read', [company_id], {'fields': ['store_website']})[0]['store_website']     
            
            # 2. Object proxy
            # models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        except Exception as e:
            ex = e
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
                    "store_url": 'https://demo.hinosoft.com' if ('a' in user.username) or (user.username == '0919933911') else 'http://192.168.104.85:5005' if (user.username== '0385249001') else 'http://192.168.10.26:5005',
                    "refresh": str(refresh),
                    "uid": uid,
                    "company_id": company_id,
                    "company_store_website": company_store_website,
                    "odoo_exception": str(ex),
                }
            )
     
        return ApiResponse.error(message="Sai tài khoản hoặc mật khẩu", status=401)



class StoreRefreshTokenView(APIView):
    """
    API: Tạo Store Refresh Token

    Endpoint:
    POST /api/store/refresh-token/

    Mô tả:
    API này cho phép superuser tạo ra một store token và refresh token dành cho một brand cụ thể. 
    Store token có thời hạn rất dài (9999 ngày), dùng để quản lý cửa hàng. Refresh token dùng để lấy access token mới.

    Yêu cầu:
    - Người gọi API phải đăng nhập và xác thực bằng JWT (access token).
    - Người gọi API phải có quyền superuser.

    Request:
    - Method: POST
    - Headers:
    Authorization: Bearer <access_token>
    Content-Type: application/json
    - Body:
    {
    "brand": "tichtru"
    }

    Response:

    1. Thành công (HTTP 200):
    {
    "success": true,
    "message": "Tạo store token thành công",
    "data": {
        "store_token": "<JWT RS256 token>",
        "refresh": "<JWT refresh token>"
    }
    }

    2. Thiếu tham số brand (HTTP 400):
    {
    "success": false,
    "message": "Thiếu tham số 'brand'",
    "data": []
    }

    3. Không có quyền (HTTP 403):
    {
    "success": false,
    "message": "Permission denied. Superuser required.",
    "data": []
    }

    Các trường dữ liệu trả về:
    - success (boolean): Trạng thái thành công hay thất bại
    - message (string): Thông điệp mô tả kết quả
    - data (object): Dữ liệu trả về khi thành công
    - store_token (string): JWT token riêng cho store, ký bằng RSA private key, thời hạn dài
    - refresh (string): Refresh token (JWT) để lấy access token mới

    Ghi chú:
    - Chỉ superuser mới có thể gọi API này.
    - Store token được gắn với brand cụ thể, dùng cho việc quản lý cửa hàng.
    """
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
