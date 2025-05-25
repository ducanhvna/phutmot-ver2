import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.jwt_helper import get_jwt_header_for_user

client = TestClient(app)

def get_admin_headers():
    user = {
        "id": 1,
        "email": "admin@example.com",
        "role": "admin",
        "is_active": True,
        "username": "admin"
    }
    return get_jwt_header_for_user(user)

# def test_create_service_plan():
#     headers = get_admin_headers()
#     data = {
#         "name": "PRO",
#         "description": "Pro plan",
#         "price": 199.0,
#         "features": "feature1,feature2"
#     }
#     res = client.post("/service/", json=data, headers=headers)
#     assert res.status_code in (200, 201)
#     plan = res.json()
#     assert plan["name"] == "PRO"
#     assert plan["price"] == 199.0

# def test_list_service_plans():
#     headers = get_admin_headers()
#     res = client.get("/service/", headers=headers)
#     assert res.status_code == 200
#     plans = res.json()
#     assert isinstance(plans, list)
#     assert any(p["name"] == "PRO" for p in plans)

# def test_create_subscription():
#     headers = get_admin_headers()
#     # Giả lập đã có user_id=1, company_id=1, plan_id=1
#     data = {
#         "user_id": 1,
#         "company_id": 1,
#         "plan_id": 1,
#         "is_active": True
#     }
#     res = client.post("/subscription/", json=data, headers=headers)
#     assert res.status_code in (200, 201)
#     sub = res.json()
#     assert sub["user_id"] == 1
#     assert sub["plan_id"] == 1

def test_get_jwt_token_header():
    from app.utils.jwt_helper import get_jwt_header_for_user
    user = {
        "id": 123,
        "email": "testuser@example.com",
        "role": "admin",
        "is_active": True,
        "username": "testuser"
    }
    headers = get_jwt_header_for_user(user)
    assert "Authorization" in headers
    assert headers["Authorization"].startswith("Bearer ")
    # Test decode token
    from jose import jwt
    token = headers["Authorization"].split(" ", 1)[1]
    payload = jwt.decode(token, "your-secret-key", algorithms=["HS256"])
    assert payload["email"] == user["email"]
    assert payload["role"] == user["role"]
    assert payload["is_active"] is True
