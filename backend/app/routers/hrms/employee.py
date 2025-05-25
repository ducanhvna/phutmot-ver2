from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.hrms.employee import (
    Employee, EmployeeLogin, EmployeeContract, EmployeeAttendance, EmployeeShift, EmployeeProject
)
from app.schemas.hrms.employee import (
    EmployeeCreate, EmployeeOut, EmployeeLoginCreate, EmployeeLoginOut,
    EmployeeContractCreate, EmployeeContractOut, EmployeeAttendanceCreate, EmployeeAttendanceOut,
    EmployeeShiftCreate, EmployeeShiftOut, EmployeeProjectCreate, EmployeeProjectOut
)

router = APIRouter(prefix="/api/hrms", tags=["hrms"])

# --- Employee ---
@router.post("/employee", response_model=EmployeeOut)
def create_employee(data: EmployeeCreate, db: Session = Depends(get_db)):
    obj = Employee(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/employee", response_model=list[EmployeeOut])
def list_employee(company_id: int, db: Session = Depends(get_db)):
    return db.query(Employee).filter(Employee.company_id == company_id).all()

# --- EmployeeLogin ---
@router.post("/employee-login", response_model=EmployeeLoginOut)
def create_employee_login(data: EmployeeLoginCreate, db: Session = Depends(get_db)):
    obj = EmployeeLogin(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/employee-login", response_model=list[EmployeeLoginOut])
def list_employee_login(company_id: int, db: Session = Depends(get_db)):
    return db.query(EmployeeLogin).filter(EmployeeLogin.company_id == company_id).all()

# --- EmployeeContract ---
@router.post("/employee-contract", response_model=EmployeeContractOut)
def create_employee_contract(data: EmployeeContractCreate, db: Session = Depends(get_db)):
    obj = EmployeeContract(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/employee-contract", response_model=list[EmployeeContractOut])
def list_employee_contract(company_id: int, month: int, year: int, db: Session = Depends(get_db)):
    return db.query(EmployeeContract).filter_by(company_id=company_id, month=month, year=year).all()

# --- EmployeeAttendance ---
@router.post("/employee-attendance", response_model=EmployeeAttendanceOut)
def create_employee_attendance(data: EmployeeAttendanceCreate, db: Session = Depends(get_db)):
    obj = EmployeeAttendance(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/employee-attendance", response_model=list[EmployeeAttendanceOut])
def list_employee_attendance(company_id: int, month: int, year: int, db: Session = Depends(get_db)):
    return db.query(EmployeeAttendance).filter_by(company_id=company_id, month=month, year=year).all()

# --- EmployeeShift ---
@router.post("/employee-shift", response_model=EmployeeShiftOut)
def create_employee_shift(data: EmployeeShiftCreate, db: Session = Depends(get_db)):
    obj = EmployeeShift(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/employee-shift", response_model=list[EmployeeShiftOut])
def list_employee_shift(company_id: int, month: int, year: int, db: Session = Depends(get_db)):
    return db.query(EmployeeShift).filter_by(company_id=company_id, month=month, year=year).all()

# --- EmployeeProject ---
@router.post("/employee-project", response_model=EmployeeProjectOut)
def create_employee_project(data: EmployeeProjectCreate, db: Session = Depends(get_db)):
    obj = EmployeeProject(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/employee-project", response_model=list[EmployeeProjectOut])
def list_employee_project(company_id: int, month: int, year: int, db: Session = Depends(get_db)):
    return db.query(EmployeeProject).filter_by(company_id=company_id, month=month, year=year).all()
