from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db import Base
from datetime import datetime

class ETLJob(Base):
    __tablename__ = "etl_jobs"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, running, success, failed
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    result = Column(JSON, nullable=True)  # Lưu kết quả ETL hoặc log lỗi
    config = Column(JSON, nullable=True)  # Thông tin kết nối, kiểu kết nối, ...
    is_active = Column(Boolean, default=True)
    company = relationship("Company")
