from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool
    is_oauth: bool
    oauth_provider: Optional[str]
    class Config:
        orm_mode = True

class CompanyBase(BaseModel):
    name: str

class CompanyCreate(CompanyBase):
    pass

class CompanyOut(CompanyBase):
    id: int
    owner_id: int
    class Config:
        orm_mode = True

class ServicePlanEnum(str, Enum):
    BASIC = "Basic"
    STANDARD = "Standard"
    PRO = "Pro"
    BUSINESS = "Business"
    ENTERPRISE = "Enterprise"

class ServicePlanOut(BaseModel):
    id: int
    name: ServicePlanEnum
    description: Optional[str]
    price: float
    features: Optional[str]
    class Config:
        orm_mode = True

class SubscriptionOut(BaseModel):
    id: int
    user_id: int
    company_id: int
    plan_id: int
    start_date: datetime
    end_date: Optional[datetime]
    is_active: bool
    class Config:
        orm_mode = True

class PaymentMethodEnum(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"

class PaymentOut(BaseModel):
    id: int
    subscription_id: int
    amount: float
    method: PaymentMethodEnum
    status: str
    created_at: datetime
    class Config:
        orm_mode = True
