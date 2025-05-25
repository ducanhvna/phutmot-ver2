import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import SessionLocal
from app.models.core import User, UserRoleEnum, Subscription, ServicePlan, Payment, PaymentMethodEnum
from passlib.hash import bcrypt

def clear_users():
    db = SessionLocal()
    db.query(User).delete()
    db.commit()
    db.close()

def clear_subscriptions():
    db = SessionLocal()
    db.query(Subscription).delete()
    db.commit()
    db.close()

def clear_service_plans():
    db = SessionLocal()
    db.query(ServicePlan).delete()
    db.commit()
    db.close()

def clear_payments():
    db = SessionLocal()
    db.query(Payment).delete()
    db.commit()
    db.close()

client = TestClient(app)

@pytest.mark.usefixtures("setup_test_db")
def test_register_user_success():
    clear_users()
    resp = client.post("/user/register", json={
        "email": "user1@example.com",
        "password": "12345678",
        "full_name": "User One"
    })
    assert resp.status_code == 200
    db = SessionLocal()
    user = db.query(User).filter_by(email="user1@example.com").first()
    assert user is not None
    assert user.full_name == "User One"
    assert user.is_active is True
    assert user.is_verified is True
    db.close()

@pytest.mark.usefixtures("setup_test_db")
def test_register_user_duplicate():
    clear_users()
    db = SessionLocal()
    db.add(User(email="user2@example.com", hashed_password=bcrypt.hash("12345678"), is_active=True))
    db.commit()
    db.close()
    resp = client.post("/user/register", json={
        "email": "user2@example.com",
        "password": "12345678",
        "full_name": "User Two"
    })
    assert resp.status_code == 400

@pytest.mark.usefixtures("setup_test_db")
def test_upgrade_plan_success():
    clear_users(); clear_service_plans(); clear_subscriptions()
    db = SessionLocal()
    user = User(email="user3@example.com", hashed_password=bcrypt.hash("12345678"), is_active=True)
    db.add(user)
    db.commit()
    plan = ServicePlan(name="Basic", price=10, description="Basic", features="")
    db.add(plan)
    db.commit()
    user_id = user.id  # Lưu id trước khi đóng session
    plan_id = plan.id
    db.close()
    resp = client.post("/user/upgrade-plan", json={"plan_id": plan_id, "user_id": user_id})
    assert resp.status_code == 200
    db = SessionLocal()
    sub = db.query(Subscription).filter_by(user_id=user_id, plan_id=plan_id).first()
    assert sub is not None
    db.close()

@pytest.mark.usefixtures("setup_test_db")
def test_update_payment_success():
    clear_users(); clear_service_plans(); clear_subscriptions(); clear_payments()
    db = SessionLocal()
    user = User(email="user4@example.com", hashed_password=bcrypt.hash("12345678"), is_active=True)
    db.add(user)
    db.commit()
    plan = ServicePlan(name="Pro", price=20, description="Pro", features="")
    db.add(plan)
    db.commit()
    sub = Subscription(user_id=user.id, plan_id=plan.id, is_active=True)
    db.add(sub)
    db.commit()
    sub_id = sub.id  # Lưu id trước khi đóng session
    db.close()
    resp = client.post("/user/update-payment", json={
        "subscription_id": sub_id,
        "amount": 20,
        "method": "online"
    })
    assert resp.status_code == 200
    db = SessionLocal()
    payment = db.query(Payment).filter_by(subscription_id=sub_id).first()
    assert payment is not None
    assert payment.amount == 20
    assert payment.method == PaymentMethodEnum.ONLINE
    db.close()

@pytest.mark.usefixtures("setup_test_db")
def test_forgot_password_success():
    clear_users()
    db = SessionLocal()
    db.add(User(email="user5@example.com", hashed_password=bcrypt.hash("12345678"), is_active=True))
    db.commit()
    db.close()
    resp = client.post("/user/forgot-password", json={"email": "user5@example.com"})
    assert resp.status_code == 200
    assert "reset link" in resp.json()["msg"]

@pytest.mark.usefixtures("setup_test_db")
def test_forgot_password_not_found():
    clear_users()
    resp = client.post("/user/forgot-password", json={"email": "notfound@example.com"})
    assert resp.status_code == 404

@pytest.mark.usefixtures("setup_test_db")
def test_reset_password_success():
    clear_users()
    db = SessionLocal()
    db.add(User(email="user6@example.com", hashed_password=bcrypt.hash("oldpass"), is_active=True))
    db.commit()
    db.close()
    resp = client.post("/user/reset-password", json={
        "email": "user6@example.com",
        "old_password": "oldpass",
        "new_password": "newpass"
    })
    assert resp.status_code == 200
    db = SessionLocal()
    user = db.query(User).filter_by(email="user6@example.com").first()
    assert bcrypt.verify("newpass", user.hashed_password)
    db.close()

@pytest.mark.usefixtures("setup_test_db")
def test_reset_password_wrong_old():
    clear_users()
    db = SessionLocal()
    db.add(User(email="user7@example.com", hashed_password=bcrypt.hash("oldpass"), is_active=True))
    db.commit()
    db.close()
    resp = client.post("/user/reset-password", json={
        "email": "user7@example.com",
        "old_password": "wrongpass",
        "new_password": "newpass"
    })
    assert resp.status_code == 400
    assert "Old password incorrect" in resp.json()["detail"]

@pytest.mark.usefixtures("setup_test_db")
def test_verify_email_success():
    clear_users()
    # Đăng ký user để lấy token xác thực
    resp = client.post("/user/register", json={
        "email": "verify@example.com",
        "password": "12345678",
        "full_name": "Verify User"
    })
    assert resp.status_code == 200
    db = SessionLocal()
    user = db.query(User).filter_by(email="verify@example.com").first()
    # Nếu không có info (do không cấu hình mail server), test auto-verified
    if not user.info or "verify_token" not in user.info:
        assert user.is_verified is True
    else:
        token = user.info["verify_token"]
        resp2 = client.get(f"/user/verify-email?token={token}&email=verify@example.com")
        assert resp2.status_code == 200
        db.refresh(user)
        assert user.is_verified is True
    db.close()


def test_verify_email_invalid_token():
    clear_users()
    resp = client.post("/user/register", json={
        "email": "verify2@example.com",
        "password": "12345678",
        "full_name": "Verify User2"
    })
    assert resp.status_code == 200
    # Gọi endpoint xác thực email với token sai
    resp2 = client.get("/user/verify-email?token=invalidtoken&email=verify2@example.com")
    assert resp2.status_code == 400
    assert "Invalid or expired token" in resp2.json()["detail"]
