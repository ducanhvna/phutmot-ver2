from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

class SummaryReportMonthlyReportBase(BaseModel):
    employee_id: Optional[int] = None
    employee_code: str
    month: int
    year: int
    info: dict = Field(default_factory=dict)
    created_by: Optional[str] = None

class SummaryReportMonthlyReportCreate(SummaryReportMonthlyReportBase):
    pass

class SummaryReportMonthlyReportOut(SummaryReportMonthlyReportBase):
    id: int
    created_at: datetime
    model_config = dict(from_attributes=True)
