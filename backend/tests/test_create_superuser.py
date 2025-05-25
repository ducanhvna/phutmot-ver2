import pytest
from app.db import SessionLocal
from app.models.core import User, UserRoleEnum
from passlib.hash import bcrypt

def clear_users():
    db = SessionLocal()
    db.query(User).delete()
    db.commit()
    db.close()

def test_create_superuser_success():
    clear_users()
    db = SessionLocal()
    email = "admin@example.com"
    password = "12345678"
    user = User(
        email=email,
        hashed_password=bcrypt.hash(password),
        full_name="Admin Root",
        is_active=True,
        is_superuser=True,
        is_staff=True,
        role=UserRoleEnum.SUPERADMIN,
        is_verified=True
    )
    db.add(user)
    db.commit()
    found = db.query(User).filter_by(email=email).first()
    assert found is not None
    assert found.is_superuser is True
    assert found.is_staff is True
    assert found.role == UserRoleEnum.SUPERADMIN
    assert found.is_verified is True
    db.close()

def test_create_superuser_duplicate():
    clear_users()
    db = SessionLocal()
    email = "admin@example.com"
    password = "12345678"
    user = User(
        email=email,
        hashed_password=bcrypt.hash(password),
        is_superuser=True,
        is_staff=True,
        role=UserRoleEnum.SUPERADMIN,
        is_verified=True
    )
    db.add(user)
    db.commit()
    # Thử tạo lại user với email trùng
    user2 = User(
        email=email,
        hashed_password=bcrypt.hash(password),
        is_superuser=True,
        is_staff=True,
        role=UserRoleEnum.SUPERADMIN,
        is_verified=True
    )
    with pytest.raises(Exception):
        db.add(user2)
        db.commit()
    db.rollback()
    db.close()
