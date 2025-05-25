from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float, Enum
from sqlalchemy.orm import relationship
from app.db import Base
from sqlalchemy.dialects.postgresql import JSONB
import enum
from datetime import datetime

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
    is_active = Column(Boolean, default=True)
    is_oauth = Column(Boolean, default=False)
    oauth_provider = Column(String, nullable=True)
    oauth_id = Column(String, nullable=True)
    role = Column(Enum(UserRoleEnum), default=UserRoleEnum.EMPLOYEE, nullable=False)
    companies = relationship("Company", back_populates="owner")
    subscriptions = relationship("Subscription", back_populates="user")
    info = Column(JSONB, nullable=True)

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="companies")
    subscriptions = relationship("Subscription", back_populates="company")
    info = Column(JSONB, nullable=True)

class ServicePlanEnum(str, enum.Enum):
    BASIC = "Basic"
    STANDARD = "Standard"
    PRO = "Pro"
    BUSINESS = "Business"
    ENTERPRISE = "Enterprise"

class ServicePlan(Base):
    __tablename__ = "service_plans"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Enum(ServicePlanEnum), unique=True, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    features = Column(String)  # JSON string or comma separated
    subscriptions = relationship("Subscription", back_populates="plan")
    info = Column(JSONB, nullable=True)

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company_id = Column(Integer, ForeignKey("companies.id"))
    plan_id = Column(Integer, ForeignKey("service_plans.id"))
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    user = relationship("User", back_populates="subscriptions")
    company = relationship("Company", back_populates="subscriptions")
    plan = relationship("ServicePlan", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription")
    info = Column(JSONB, nullable=True)

class PaymentMethodEnum(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    amount = Column(Float, nullable=False)
    method = Column(Enum(PaymentMethodEnum), nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    subscription = relationship("Subscription", back_populates="payments")
    info = Column(JSONB, nullable=True)
