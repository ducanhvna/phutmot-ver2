from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

class FileMetadataBase(BaseModel):
    company_id: int
    report_type: str
    file_url: str
    file_name: str
    created_by: Optional[str] = None
    info: dict = Field(default_factory=dict)

class FileMetadataCreate(FileMetadataBase):
    pass

class FileMetadataOut(FileMetadataBase):
    id: int
    created_at: datetime
    model_config = dict(from_attributes=True)
