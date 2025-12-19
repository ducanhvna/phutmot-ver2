from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from .serializers import UserSerializer
import xmlrpc.client
from django.conf import settings

class UserRegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        email = serializer.validated_data['email']
        domain = email.split('@')[-1]
        username = domain.split('.')[0]  # Create username based on email domain
        unique_key = get_random_string(length=8)  # Generate unique 8-character key

        # Here you would connect to the Odoo server for user validation and password management
        odoo_response = self.validate_user_with_odoo(email, unique_key)
        print("Odoo response:", odoo_response)
        if odoo_response['status'] == 'success':
            user = serializer.save(username=username)
            user.unique_key = unique_key
            user.save()
            refresh = RefreshToken.for_user(user)
            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        else:
            raise Exception("User validation with Odoo failed.")

    def validate_user_with_odoo(self, username, new_password):
        """
        Kiểm tra user trên Odoo, tạo mới nếu chưa có, đổi mật khẩu về unique_key bằng xmlrpc
        """
        ODOO_URL = settings.ODDO_SERVER_URL
        ODOO_DB =  settings.ODDO_DB
        ODOO_USER = settings.ODDO_USERNAME
        ODOO_PASS = settings.ODDO_USERNAME
        # 1. Authenticate
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
        if not uid:
            return {'status': 'fail', 'msg': 'Odoo login failed'}

        # 2. Object proxy
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

        # 3. Search user by login
        user_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASS,
            'res.users', 'search',
            [[['login', '=', username]]]
        )

        # 4. If not exists, create user
        if not user_ids:
            user_id = models.execute_kw(
                ODOO_DB, uid, ODOO_PASS,
                'res.users', 'create',
                [{
                    'login': username,
                    'name': username,
                    'password': new_password
                }]
            )
        else:
            user_id = user_ids[0]

        # 5. Update password to new_password
        result = models.execute_kw(
            ODOO_DB, uid, ODOO_PASS,
            'res.users', 'write',
            [[user_id], {'new_password': new_password}]
        )
        if result:
            return {'status': 'success'}
        else:
            return {'status': 'fail', 'msg': 'Update password failed'}

