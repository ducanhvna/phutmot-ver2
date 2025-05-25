from fastapi import APIRouter, HTTPException, Depends, Body, Request, BackgroundTasks
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.core import User, UserRoleEnum, Subscription, ServicePlan, Payment, PaymentMethodEnum
from passlib.hash import bcrypt
from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr
import os
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/user", tags=["user"])

MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "HRMS")
APP_NAME = os.getenv("APP_NAME", "HRMS")
MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() == "true"

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UpgradePlanRequest(BaseModel):
    plan_id: int
    user_id: int

class UpdatePaymentRequest(BaseModel):
    subscription_id: int
    amount: float
    method: PaymentMethodEnum

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str
    old_password: str | None = None
    token: str | None = None  # Nếu dùng xác thực qua email

def send_verify_email(to_email, verify_link):
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        msg = MIMEMultipart()
        msg["From"] = f"{MAIL_FROM_NAME} <{MAIL_FROM}>"
        msg["To"] = to_email
        msg["Subject"] = f"Xác thực tài khoản {APP_NAME}"
        body = f"Chào bạn,\n\nVui lòng xác thực tài khoản bằng link sau: {verify_link}\n\nTrân trọng,\n{MAIL_FROM_NAME}"
        msg.attach(MIMEText(body, "plain"))
        if MAIL_USE_SSL:
            server = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
        else:
            server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
            if MAIL_USE_TLS:
                server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.sendmail(MAIL_FROM, to_email, msg.as_string())
        server.quit()
        print(f"[OK] Sent verify email to {to_email}")
    except Exception as e:
        print(f"[ERROR] Failed to send verify email: {e}")

@router.post("/register")
def register_user(data: UserRegisterRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db), request: Request = None):
    if db.query(User).filter_by(email=data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    user = User(
        email=data.email,
        hashed_password=bcrypt.hash(data.password),
        full_name=data.full_name,
        is_active=True,
        is_verified=False,
        role=UserRoleEnum.EMPLOYEE
    )
    if MAIL_SERVER and MAIL_FROM:
        db.add(user)
        db.commit()
        token = f"verify-{user.id}-{int(datetime.now(timezone.utc).timestamp())}"
        user.info = {"verify_token": token}
        db.commit()
        base_url = str(request.base_url) if request else "http://localhost:8000/"
        verify_link = f"{base_url.rstrip('/').replace('/docs','')}/user/verify-email?token={token}&email={user.email}"
        background_tasks.add_task(send_verify_email, user.email, verify_link)
        return {"msg": "User registered. Please check your email to verify.", "verify_link": verify_link}
    else:
        user.is_verified = True
        db.add(user)
        db.commit()
        return {"msg": "User registered and auto-verified (no mail server)"}

@router.post("/upgrade-plan")
def upgrade_plan(data: UpgradePlanRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    plan = db.query(ServicePlan).filter_by(id=data.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    sub = Subscription(user_id=user.id, plan_id=plan.id, start_date=datetime.now(timezone.utc), is_active=True)
    db.add(sub)
    db.commit()
    return {"msg": "Plan upgraded", "plan": plan.name}

@router.post("/update-payment")
def update_payment(data: UpdatePaymentRequest, db: Session = Depends(get_db)):
    sub = db.query(Subscription).filter_by(id=data.subscription_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    payment = Payment(subscription_id=sub.id, amount=data.amount, method=data.method, status="completed", created_at=datetime.now(timezone.utc))
    db.add(payment)
    db.commit()
    return {"msg": "Payment updated"}

@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # TODO: Gửi email reset password (tùy tích hợp SMTP)
    return {"msg": "Password reset link sent to email (mock)"}

@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Nếu có old_password thì xác thực đổi trực tiếp
    if data.old_password:
        if not bcrypt.verify(data.old_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Old password incorrect")
        user.hashed_password = bcrypt.hash(data.new_password)
        db.commit()
        return {"msg": "Password changed successfully"}
    # Nếu có token (quên mật khẩu), xác thực token (mock)
    if data.token:
        # TODO: xác thực token nếu có tích hợp email
        user.hashed_password = bcrypt.hash(data.new_password)
        db.commit()
        return {"msg": "Password reset successfully"}
    raise HTTPException(status_code=400, detail="Missing old_password or token")

@router.get("/verify-email")
def verify_email(token: str, email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=email).first()
    if not user or not user.info or user.info.get("verify_token") != token:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user.is_verified = True
    db.commit()
    return {"msg": "Email verified successfully"}
