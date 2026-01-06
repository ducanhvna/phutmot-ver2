import random, string, requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from apps.common.utils.api_response import ApiResponse
from django.contrib.auth import authenticate
import jwt
from rest_framework.views import APIView
# from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.conf import settings
import jwt, os
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
# Load private key
with open("private.pem", "r") as f:
    PRIVATE_KEY = f.read()

def generate_password():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(6))

def odoo_rpc_call(service, method, args):
    """Gọi Odoo RPC cũ để search/read"""
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": service,
            "method": method,
            "args": args
        },
        "id": 1
    }
    resp = requests.post(settings.ODOO_SERVER_URL + "/jsonrpc",
                         json=payload,
                         headers={"Content-Type": "application/json"})
    resp.raise_for_status()
    return resp.json()

def odoo_api_set_password(user_id, new_pass):
    """Đổi mật khẩu qua API mới của Odoo 19"""
    url = f"{settings.ODOO_SERVER_URL}/json/2/res.users/set_password"
    headers = {
        "Authorization": f"Bearer {settings.ODOO_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"args": [user_id, new_pass]}
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()

def odoo_admin_authenticate():
    return odoo_rpc_call("common", "authenticate", [
        settings.ODOO_DB, settings.ODOO_USERNAME, settings.ODOO_PASSWORD, {}
    ]).get("result")

class LoginView(APIView):
    """
    API: Đăng nhập hệ thống

    Endpoint:
    POST /auth/token

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
        inventory_code = 'FS01'
        try:
            ODOO_SERVER_URL = settings.ODOO_SERVER_URL
            ODOO_DB =  settings.ODOO_DB
            ODOO_USERNAME = settings.ODOO_USERNAME
            ODOO_PASSWORD = settings.ODOO_PASSWORD
            # 1. Authenticate
            common = xmlrpc.client.ServerProxy(f'{ODOO_SERVER_URL}/xmlrpc/2/common')
            uid = common.authenticate(ODOO_DB, username, password, {})
            if not uid:
                # Tim kiem username trong odoo khong thay thi tra ve loi uid
                model = xmlrpc.client.ServerProxy(f'{ODOO_SERVER_URL}/xmlrpc/2/object')
                user_ids = model.execute_kw(
                    ODOO_DB,
                    settings.ODOO_ADMIN_UID,
                    ODOO_PASSWORD,
                    'res.users',
                    'search',
                    [[ '|', ('login', '=', username), ('email', '=', username) ]]
                )

                if len(user_ids)>0:
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
            models = xmlrpc.client.ServerProxy(f"{ODOO_SERVER_URL}/xmlrpc/2/object")

            user_info = models.execute_kw(
                ODOO_DB, settings.ODDO_ADMIN_UID, ODOO_PASSWORD,
                'res.users', 'read',
                [uid],
                {'fields': ['company_id', 'x_pos_shop_ids']}
            )[0]['company_id'][0]
            company_id = user_info[0]['company_id'][0]
            company_store_website = models.execute_kw(ODOO_DB, settings.ODDO_ADMIN_UID, ODOO_PASSWORD,
                'res.company', 'read', [company_id], {'fields': ['website']})[0]['website']     
            shop_ids = user_info[0]['x_pos_shop_ids']
            # 2. Object proxy
            # models = xmlrpc.client.ServerProxy(f'{ODOO_SERVER_URL}/xmlrpc/2/object')
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
            company_store_website = "http://14.224.192.52:8889" if (user.username == '0919933911') else "https://btmherp.baotinmanhhai.vn"
            shop_id = None
            config_id = None
            session_id = None
            try:
                models = xmlrpc.client.ServerProxy(f"{ODOO_SERVER_URL}/xmlrpc/2/object")

                # shop_ids = self.odoo.search("pos.shop", [('code', '=', self.warhouse_code)], 1)
                # if shop_ids and len(shop_ids) > 0:
                #     shop_id = shop_ids[0][0]
                #     inventory_code = models.execute_kw(
                #         ODOO_DB,
                #         settings.ODOO_ADMIN_UID,
                #         ODOO_PASSWORD,
                #         "pos.shop",
                #         'read',
                #         [shop_id],
                #         {'fields': ['code']}
                #     )[0]['code']
                    # config_ids = self.odoo.search("pos.config", [('x_pos_shop_id', '=', shop_id)], limit=1)
                    # config_ids = models.execute_kw(
                    #     ODOO_DB,
                    #     settings.ODOO_ADMIN_UID,
                    #     ODOO_PASSWORD,
                    #     "pos.config",
                    #     'search',
                    #     [[ ('x_pos_shop_id', '=', shop_id) ]]
                    # )
                    # if config_ids and len(config_ids) >0:
                    #     config_id = config_ids[0]
                session_ids = models.execute_kw(
                    ODOO_DB,
                    settings.ODOO_ADMIN_UID,
                    ODOO_PASSWORD,
                    "pos.session",
                    "search",
                    [[
                        ("x_pos_user_ids", "in", [uid]),
                        ("state", "=", "opened"),
                    ]]
                )

                if session_ids and len(session_ids) >0:
                    session_id = session_ids[0]
                    try:
                        config_id = models.execute_kw(
                            ODOO_DB,
                            settings.ODOO_ADMIN_UID,
                            ODOO_PASSWORD,
                            "pos.session",
                            'read',
                            [shop_id],
                            {'fields': ['config_id']}
                        )[0]['config_id'][0]
                        shop_id = models.execute_kw(
                            ODOO_DB,
                            settings.ODOO_ADMIN_UID,
                            ODOO_PASSWORD,
                            "pos.config",
                            'read',
                            [shop_id],
                            {'fields': ['x_pos_shop_id']}
                        )[0]['x_pos_shop_id'][0]
                        inventory_code = models.execute_kw(
                            ODOO_DB,
                            settings.ODOO_ADMIN_UID,
                            ODOO_PASSWORD,
                            "pos.shop",
                            'read',
                            [shop_id],
                            {'fields': ['code']}
                        )[0]['code']
                    except Exception as exsession:
                        pass
            except Exception as e:
                ex = e
            
            store_url = os.getenv(f'STORE_URL_{inventory_code}',default='https://demo.hinosoft.com')
            
            return ApiResponse.success(
                message="Đăng nhập thành công",
                data= {
                    "store_token": token,
                    "access": str(refresh.access_token),
                    "printers": ['tichtru', 'tho', 'trangsuc'],
                    "store_url": store_url,
                    "refresh": str(refresh),
                    "uid": uid,
                    "shop_id": shop_id,
                    "config_id": config_id,
                    "company_id": company_id,
                    "session_id": session_id,
                    "company_store_website": company_store_website,
                    "odoo_db": "btmh_erp",
                    "odoo_exception": str(ex),
                }
            )
     
        return ApiResponse.error(message="Sai tài khoản hoặc mật khẩu", status=401)

