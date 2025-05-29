from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, ForeignKey, JSON
from app.db import Base, engine
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.core import Company
# Tương thích JSON/JSONB cho SQLite và Postgres
try:
    from sqlalchemy.dialects.postgresql import JSONB
    if engine.url.get_backend_name() == "postgresql":
        JSONType = JSONB
    else:
        JSONType = JSON
except ImportError:
    JSONType = JSON

class SummaryReportMonthlyReport(Base):
    __tablename__ = "hrms_summary_report_monthly"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)
    company = relationship("Company")
    month = Column(Integer, index=True)
    year = Column(Integer, index=True)
    info = Column(JSONType)  # Lưu thông tin link file report, metadata, ...
    created_by = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    __table_args__ = (UniqueConstraint("company_id", "month", "year", name="uq_summary_report_monthly"),)
