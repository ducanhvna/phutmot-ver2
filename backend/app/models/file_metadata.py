from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.sql import func
from app.db import Base

class FileMetadata(Base):
    __tablename__ = "file_metadata"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)
    report_type = Column(String, index=True)
    file_url = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(String)
    info = Column(JSON, default={})
    __table_args__ = (UniqueConstraint("company_id", "report_type", "file_name", name="uq_file_metadata"),)
