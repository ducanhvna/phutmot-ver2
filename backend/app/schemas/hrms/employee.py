from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

class EmployeeBase(BaseModel):
    employee_code: str
    company_id: int
    info: dict = Field(default_factory=dict)
    created_by: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeOut(EmployeeBase):
    id: int
    created_at: datetime
    model_config = dict(from_attributes=True)

class EmployeeLoginBase(BaseModel):
    employee_code: str
    company_id: int
    info: dict = Field(default_factory=dict)
    created_by: Optional[str] = None

class EmployeeLoginCreate(EmployeeLoginBase):
    pass

class EmployeeLoginOut(EmployeeLoginBase):
    id: int
    created_at: datetime
    model_config = dict(from_attributes=True)

class EmployeeContractBase(BaseModel):
    employee_code: str
    company_id: int
    month: int
    year: int
    info: dict = Field(default_factory=dict)
    created_by: Optional[str] = None

class EmployeeContractCreate(EmployeeContractBase):
    pass

class EmployeeContractOut(EmployeeContractBase):
    id: int
    created_at: datetime
    model_config = dict(from_attributes=True)

class EmployeeAttendanceBase(BaseModel):
    employee_code: str
    company_id: int
    month: int
    year: int
    info: dict = Field(default_factory=dict)
    created_by: Optional[str] = None

class EmployeeAttendanceCreate(EmployeeAttendanceBase):
    pass

class EmployeeAttendanceOut(EmployeeAttendanceBase):
    id: int
    created_at: datetime
    model_config = dict(from_attributes=True)

class EmployeeShiftBase(BaseModel):
    employee_code: str
    company_id: int
    month: int
    year: int
    info: dict = Field(default_factory=dict)
    created_by: Optional[str] = None

class EmployeeShiftCreate(EmployeeShiftBase):
    pass

class EmployeeShiftOut(EmployeeShiftBase):
    id: int
    created_at: datetime
    model_config = dict(from_attributes=True)

class EmployeeProjectBase(BaseModel):
    employee_code: str
    company_id: int
    month: int
    year: int
    info: dict = Field(default_factory=dict)
    created_by: Optional[str] = None

class EmployeeProjectCreate(EmployeeProjectBase):
    pass

class EmployeeProjectOut(EmployeeProjectBase):
    id: int
    created_at: datetime
    model_config = dict(from_attributes=True)
