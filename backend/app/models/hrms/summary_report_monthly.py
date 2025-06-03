from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, ForeignKey, JSON
from app.db import Base, engine
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.core import Company
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from app.models.core import Company
from sqlalchemy.dialects.postgresql import insert
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
    company_id = Column(Integer, index=True)  # Thêm trường company_id
    employee_code = Column(String, index=True)
    month = Column(Integer, index=True)
    year = Column(Integer, index=True)
    info = Column(JSONType)  # Lưu thông tin link file report, metadata, ...
    created_by = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    __table_args__ = (UniqueConstraint("company_id", "employee_code", "month", "year", name="uq_summary_report_monthly"),)


def bulk_upsert_summary_report_dict_to_db(summary_report_dict: dict, db: Session, created_by=None, month=None, year=None, batch_size=400):
    """
    Bulk upsert summary_report_dict vào bảng SummaryReportMonthlyReport theo batch để tránh OOM.
    - key là employee_code
    - info: value của dict
    - Nếu trùng (company_id, employee_code, month, year) thì update info
    """
    from sqlalchemy import text
    db.execute(text(
        "SELECT setval('hrms_summary_report_monthly_id_seq', (SELECT COALESCE(MAX(id), 1) FROM hrms_summary_report_monthly))"
    ))
    from app.models.core import Company
    company = db.query(Company).filter(Company.name == 'APEC GROUP').first()
    if not company:
        company = db.query(Company).first()
    if not company:
        raise Exception("No company found in DB!")
    company_id = company.id
    print(f"Upserting {len(summary_report_dict)} month {month} year {year} summary reports to DB for company_id={company_id}...")
    to_upsert = []
    for employee_code, info in summary_report_dict.items():
        if not employee_code or not isinstance(employee_code, str):
            continue
        if employee_code.lower() in ["hrms", "summary", "report", "metadata", "info"]:
            continue
        to_upsert.append({
            'company_id': company_id,
            'employee_code': employee_code,
            'month': month,
            'year': year,
            'info': info,
            'created_by': created_by or 'etl',
        })
    total = len(to_upsert)
    for i in range(0, total, batch_size):
        batch = to_upsert[i:i+batch_size]
        stmt = insert(SummaryReportMonthlyReport).values(batch)
        update_dict = {c.name: c for c in stmt.excluded if c.name not in ['company_id', 'employee_code', 'month', 'year']}
        stmt = stmt.on_conflict_do_update(
            index_elements=['company_id', 'employee_code', 'month', 'year'],
            set_=update_dict
        )
        db.execute(stmt)
        db.commit()
        print(f"Upserted batch {i//batch_size+1} ({len(batch)} records)")
