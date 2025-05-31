from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, ForeignKey, JSON
from app.db import Base, engine
# Tương thích JSON/JSONB cho SQLite và Postgres
try:
    from sqlalchemy.dialects.postgresql import JSONB
    if engine.url.get_backend_name() == "postgresql":
        JSONType = JSONB
    else:
        JSONType = JSON
except ImportError:
    JSONType = JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from app.models.core import Company

class Employee(Base):
    __tablename__ = "hrms_employee"
    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String, index=True)
    company_id = Column(Integer, index=True)
    info = Column(JSONType)  # Thông tin nhân viên dạng mở rộng
    created_by = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    __table_args__ = (UniqueConstraint("employee_code", "company_id", name="uq_employee_code_company"),)

class EmployeeLogin(Base):
    __tablename__ = "hrms_employee_login"
    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String, index=True)
    company_id = Column(Integer, index=True)
    info = Column(JSONType)  # Thông tin đăng nhập (username, password hash, ...)
    created_by = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    __table_args__ = (UniqueConstraint("employee_code", "company_id", name="uq_employee_login_code_company"),)

class EmployeeContract(Base):
    __tablename__ = "hrms_employee_contract"
    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String, index=True)
    company_id = Column(Integer, index=True)
    month = Column(Integer)
    year = Column(Integer)
    info = Column(JSONType)  # Thông tin hợp đồng dạng mở rộng
    created_by = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    __table_args__ = (UniqueConstraint("employee_code", "month", "year", "company_id", name="uq_employee_contract"),)

class EmployeeAttendance(Base):
    __tablename__ = "hrms_employee_attendance"
    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String, index=True)
    company_id = Column(Integer, index=True)
    month = Column(Integer)
    year = Column(Integer)
    info = Column(JSONType)  # Thông tin chấm công dạng mở rộng
    created_by = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    __table_args__ = (UniqueConstraint("employee_code", "month", "year", "company_id", name="uq_employee_attendance"),)

class EmployeeShift(Base):
    __tablename__ = "hrms_employee_shift"
    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String, index=True)
    company_id = Column(Integer, index=True)
    month = Column(Integer)
    year = Column(Integer)
    info = Column(JSONType)  # Thông tin phân ca dạng mở rộng
    created_by = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    __table_args__ = (UniqueConstraint("employee_code", "month", "year", "company_id", name="uq_employee_shift"),)

class EmployeeProject(Base):
    __tablename__ = "hrms_employee_project"
    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String, index=True)
    company_id = Column(Integer, index=True)
    month = Column(Integer)
    year = Column(Integer)
    info = Column(JSONType)  # Thông tin dự án dạng mở rộng
    created_by = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    __table_args__ = (UniqueConstraint("employee_code", "month", "year", "company_id", name="uq_employee_project"),)

def bulk_upsert_employees_dict_to_db(employees_dict: dict, db: Session, created_by=None):
    """
    Bulk upsert employees_dict vào bảng Employee.
    - employee_code là key
    - company_id: lấy company có name='APEC', nếu không có thì lấy company đầu tiên
    - info: value của dict
    - Nếu trùng (employee_code, company_id) thì update info
    """
    # Lấy company_id
    company = db.query(Company).filter(Company.name == 'APEC GROUP').first()
    if not company:
        company = db.query(Company).first()
    if not company:
        raise Exception("No company found in DB!")
    company_id = company.id
    from sqlalchemy.dialects.postgresql import insert
    to_upsert = []
    for employee_code, value in employees_dict.items():
        # Lưu info là dict có key 'profiles' chứa list các hồ sơ
        to_upsert.append({
            'employee_code': employee_code,
            'company_id': company_id,
            'info': value,  # value = {'profiles': [...]}
            'created_by': created_by or 'etl',
        })
    stmt = insert(Employee).values(to_upsert)
    update_dict = {c.name: c for c in stmt.excluded if c.name not in ['employee_code', 'company_id']}
    stmt = stmt.on_conflict_do_update(
        index_elements=['employee_code', 'company_id'],
        set_=update_dict
    )
    db.execute(stmt)
    db.commit()
