import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser

# Load public key
with open("public.pem", "r") as f:
    PUBLIC_KEY = f.read()

class ExternalUser:
    """Đại diện cho user từ hệ thống tổng, không cần tồn tại trong DB"""
    def __init__(self, username):
        self.username = username
        self.is_authenticated = True  # DRF sẽ check cái này

    def __str__(self):
        return self.username

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
            username = payload.get("sub")
            if not username:
                raise AuthenticationFailed("Invalid payload: missing sub")
            user = ExternalUser(username)
            return (user, None)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")
