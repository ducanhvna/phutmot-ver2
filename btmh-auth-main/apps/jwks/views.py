from django.http import JsonResponse
from django.conf import settings
import base64
from cryptography.hazmat.primitives import serialization

def b64url(x: bytes) -> str:
    return base64.urlsafe_b64encode(x).rstrip(b'=').decode('ascii')

def jwks_view(request):
    # Chuyển public.pem sang JWK (RSA n/e)
    pub = serialization.load_pem_public_key(settings.PUBLIC_KEY.encode("utf-8"))
    numbers = pub.public_numbers()
    n = numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, 'big')
    e = numbers.e.to_bytes((numbers.e.bit_length() + 7) // 8, 'big')
    jwk = {
        "kty": "RSA",
        "kid": "key-1",          # kid cố định cho demo, có thể sinh động để xoay khóa
        "use": "sig",
        "alg": "RS256",
        "n": b64url(n),
        "e": b64url(e),
    }
    resp = JsonResponse({"keys": [jwk]})
    resp["Cache-Control"] = "public, max-age=1800"
    return resp
