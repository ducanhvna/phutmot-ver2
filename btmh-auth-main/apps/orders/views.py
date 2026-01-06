from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import jwt
from jwt import PyJWKClient

JWKS_URL = "https://auth.example.com/.well-known/jwks.json"  # trỏ tới JWKS của auth
ISSUER = "https://auth.example.com"

jwk_client = PyJWKClient(JWKS_URL)

def verify_token(token: str):
    signing_key = jwk_client.get_signing_key_from_jwt(token).key
    payload = jwt.decode(
        token,
        signing_key,
        algorithms=["RS256"],
        issuer=ISSUER,
        options={"require": ["exp", "iat"]}
    )
    return payload

class OrderListView(APIView):
    def get(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(" ")[1]
        try:
            claims = verify_token(token)
        except Exception:
            return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({"orders": ["order1", "order2"], "user": claims.get("sub")})
