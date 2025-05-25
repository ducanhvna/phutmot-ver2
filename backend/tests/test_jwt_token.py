import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.jwt_helper import get_jwt_header_for_user

client = TestClient(app)

def get_admin_user():
    return {
        "id": 1,
        "email": "admin@example.com",
        "role": "admin",
        "is_active": True,
        "username": "admin"
    }

def test_get_jwt_token_api():
    user = get_admin_user()
    headers = get_jwt_header_for_user(user)
    # Giả lập API get token (nếu có route), hoặc kiểm tra token hợp lệ
    assert headers["Authorization"].startswith("Bearer ")
    token = headers["Authorization"][7:]
    assert len(token) > 10
    # Có thể decode lại để kiểm tra payload nếu muốn
    from jose import jwt
    from app.utils.jwt_helper import SECRET_KEY, ALGORITHM
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["email"] == user["email"]
    assert payload["role"] == user["role"]
