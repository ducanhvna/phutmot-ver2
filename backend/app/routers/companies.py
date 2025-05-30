from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.core import Company
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/companies", tags=["companies"])

class CompanyOut(BaseModel):
    id: int
    name: str
    owner_id: Optional[int] = None
    info: Optional[dict] = None
    class Config:
        from_attributes = True

@router.get("/", response_model=List[CompanyOut])
def list_companies(db: Session = Depends(get_db)):
    return db.query(Company).all()
