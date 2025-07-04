from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.schemas.core import UserCreate, UserOut
from app.models.core import User
from app.utils.auth import get_password_hash, verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.utils.education.realtendant import odoo_login

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password, full_name=user.full_name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    expires_delta = timedelta(days=30)  # 30 ngày giống frontend
    expires_at = (datetime.utcnow() + expires_delta).isoformat() + "Z"
    access_token = create_access_token({"sub": user.email}, expires_delta=expires_delta)
    user_info = {
        "name": user.full_name or user.email,
        "email": user.email,
        "roles": [user.role] if hasattr(user, "role") and user.role else ["user"],
        "avatar": f"https://i.pravatar.cc/150?img={user.id % 70}",
    }
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": expires_at,
        "user": user_info,
    }

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict

@router.post("/token", response_model=TokenResponse)
def auth_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        uid, _, _ = odoo_login(username=form_data.username, password=form_data.password)
    except Exception:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    expires_delta = timedelta(days=30)
    expires_in = int(expires_delta.total_seconds())
    access_token = create_access_token({"sub": form_data.username}, expires_delta=expires_delta)
    refresh_token = create_access_token({"sub": form_data.username, "type": "refresh"}, expires_delta=expires_delta)
    user_info = {
        "name": form_data.username,
        "email": form_data.username,
        "roles": ["teacher"],
        "uid": uid,
    }
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "user": user_info,
    }
