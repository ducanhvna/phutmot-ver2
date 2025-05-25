from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class ETLJobBase(BaseModel):
    company_id: int
    name: str
    config: Optional[Any] = None
    is_active: Optional[bool] = True

class ETLJobCreate(ETLJobBase):
    pass

class ETLJobOut(ETLJobBase):
    id: int
    status: str
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    result: Optional[Any]
    model_config = dict(from_attributes=True)
