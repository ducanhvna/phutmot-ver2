from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float, Enum, JSON
from sqlalchemy.orm import relationship
from app.db import Base, engine
import enum
from datetime import datetime, timezone

# Tương thích JSON/JSONB cho SQLite và Postgres
try:
    from sqlalchemy.dialects.postgresql import JSONB
    if engine.url.get_backend_name() == "postgresql":
        JSONType = JSONB
    else:
        JSONType = JSON
except ImportError:
    JSONType = JSON

class UserRoleEnum(str, enum.Enum):
    ADMIN = "admin"           # Quản trị công ty
    EMPLOYEE = "employee"     # Nhân viên công ty
    BUYER = "buyer"           # Người mua hàng
    SUPERADMIN = "superadmin" # Quản lý hệ thống chung

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    is_oauth = Column(Boolean, default=False)
    oauth_provider = Column(String, nullable=True)
    oauth_id = Column(String, nullable=True)
    role = Column(Enum(UserRoleEnum), default=UserRoleEnum.EMPLOYEE, nullable=False, index=True)
    is_superuser = Column(Boolean, default=False, index=True)  # Quyền full hệ thống
    is_staff = Column(Boolean, default=False, index=True)      # Quyền quản trị nội bộ (giống Django)
    last_login = Column(DateTime, nullable=True)               # Lưu thời điểm đăng nhập cuối
    date_joined = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    companies = relationship("Company", back_populates="owner")
    subscriptions = relationship("Subscription", back_populates="user")
    info = Column(JSONType, nullable=True)
    phone = Column(String, nullable=True, index=True)
    avatar = Column(String, nullable=True)  # URL hoặc path ảnh đại diện
    address = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False, index=True)  # Đã xác thực email/phone
    # Có thể mở rộng thêm các trường khác nếu cần

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), index=True)
    owner = relationship("User", back_populates="companies")
    subscriptions = relationship("Subscription", back_populates="company")
    info = Column(JSONType, nullable=True)

class ServicePlanEnum(str, enum.Enum):
    BASIC = "Basic"
    STANDARD = "Standard"
    PRO = "Pro"
    BUSINESS = "Business"
    ENTERPRISE = "Enterprise"

class ServicePlan(Base):
    __tablename__ = "service_plans"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Enum(ServicePlanEnum), unique=True, nullable=False, index=True)
    description = Column(String)
    price = Column(Float, nullable=False)
    features = Column(String)  # JSON string or comma separated
    subscriptions = relationship("Subscription", back_populates="plan")
    info = Column(JSONType, nullable=True)

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)
    plan_id = Column(Integer, ForeignKey("service_plans.id"), index=True)
    start_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    user = relationship("User", back_populates="subscriptions")
    company = relationship("Company", back_populates="subscriptions")
    plan = relationship("ServicePlan", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription")
    info = Column(JSONType, nullable=True)

class PaymentMethodEnum(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), index=True)
    amount = Column(Float, nullable=False)
    method = Column(Enum(PaymentMethodEnum), nullable=False, index=True)
    status = Column(String, default="pending", index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    subscription = relationship("Subscription", back_populates="payments")
    info = Column(JSONType, nullable=True)
