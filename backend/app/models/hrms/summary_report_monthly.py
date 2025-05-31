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
    employee_id = Column(Integer, ForeignKey("hrms_employee.id"), index=True, nullable=True)
    employee = relationship("Employee")
    employee_code = Column(String, index=True)
    month = Column(Integer, index=True)
    year = Column(Integer, index=True)
    info = Column(JSONType)  # Lưu thông tin link file report, metadata, ...
    created_by = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    __table_args__ = (UniqueConstraint("employee_id", "month", "year", name="uq_summary_report_monthly"),)

def bulk_upsert_summary_report_dict_to_db(summary_report_dict: dict, db: Session, created_by=None, month=None, year=None):
    """
    Bulk upsert summary_report_dict vào bảng SummaryReportMonthlyReport.
    - key là employee_code
    - info: value của dict
    - Nếu trùng (employee_id, month, year) thì update info
    """
    # Lấy công ty APEC GROUP (hoặc công ty đầu tiên)
    company = db.query(Company).filter(Company.name == 'APEC GROUP').first()
    if not company:
        company = db.query(Company).first()
    if not company:
        raise Exception("No company found in DB!")
    # Lấy tất cả employee của công ty đó
    from app.models.hrms.employee import Employee
    employees = db.query(Employee).filter(Employee.company_id == company.id).all()
    emp_code_to_id = {e.employee_code: e.id for e in employees}
    to_upsert = []
    for employee_code, info in summary_report_dict.items():
        employee_id = emp_code_to_id.get(employee_code)
        to_upsert.append({
            'employee_id': employee_id,
            'employee_code': employee_code,
            'month': month,
            'year': year,
            'info': info,
            'created_by': created_by or 'etl',
        })
    stmt = insert(SummaryReportMonthlyReport).values(to_upsert)
    update_dict = {c.name: c for c in stmt.excluded if c.name not in ['employee_id', 'month', 'year']}
    stmt = stmt.on_conflict_do_update(
        index_elements=['employee_id', 'month', 'year'],
        set_=update_dict
    )
    db.execute(stmt)
    db.commit()
