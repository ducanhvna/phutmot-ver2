from fastapi import APIRouter, HTTPException, Depends, Query, Header
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.hrms.employee import Employee, EmployeeLogin, EmployeeContract, EmployeeAttendance, EmployeeShift, EmployeeProject
from app.utils.buyer_jwt import decode_buyer_token

employee_info_router = APIRouter(prefix="/api/hrms", tags=["hrms-employee-info"])

def get_token_info(authorization: str):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ", 1)[1]
    buyer = decode_buyer_token(token)
    if not buyer:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return buyer["employee_code"], buyer["company_id"]

@employee_info_router.get("/employee/info")
def get_employee_info(authorization: str = Header(...), db: Session = Depends(get_db)):
    employee_code, company_id = get_token_info(authorization)
    employee = db.query(Employee).filter_by(employee_code=employee_code, company_id=company_id).first()
    return employee.info if employee else None

@employee_info_router.get("/employee-login/info")
def get_employee_login_info(
    month: int = Query(None),
    year: int = Query(None),
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    employee_code, company_id = get_token_info(authorization)
    if month is not None and year is not None:
        # Trả về info contract nếu có month/year
        contract = db.query(EmployeeContract).filter_by(employee_code=employee_code, company_id=company_id, month=month, year=year).first()
        return contract.info if contract else None
    login = db.query(EmployeeLogin).filter_by(employee_code=employee_code, company_id=company_id).first()
    return login.info if login else None

@employee_info_router.get("/employee-login/info/noauth")
def get_employee_login_info_noauth(authorization: str = Header(...), db: Session = Depends(get_db)):
    employee_code, company_id = get_token_info(authorization)
    login = db.query(EmployeeLogin).filter_by(employee_code=employee_code, company_id=company_id).first()
    return login.info if login else None

@employee_info_router.get("/employee-contract/info")
def get_employee_contract_info(month: int = Query(...), year: int = Query(...), authorization: str = Header(...), db: Session = Depends(get_db)):
    employee_code, company_id = get_token_info(authorization)
    contract = db.query(EmployeeContract).filter_by(employee_code=employee_code, company_id=company_id, month=month, year=year).first()
    return contract.info if contract else None

@employee_info_router.get("/employee-attendance/info")
def get_employee_attendance_info(month: int = Query(...), year: int = Query(...), authorization: str = Header(...), db: Session = Depends(get_db)):
    employee_code, company_id = get_token_info(authorization)
    attendance = db.query(EmployeeAttendance).filter_by(employee_code=employee_code, company_id=company_id, month=month, year=year).first()
    return attendance.info if attendance else None

@employee_info_router.get("/employee-shift/info")
def get_employee_shift_info(month: int = Query(...), year: int = Query(...), authorization: str = Header(...), db: Session = Depends(get_db)):
    employee_code, company_id = get_token_info(authorization)
    shift = db.query(EmployeeShift).filter_by(employee_code=employee_code, company_id=company_id, month=month, year=year).first()
    return shift.info if shift else None

@employee_info_router.get("/employee-project/info")
def get_employee_project_info(month: int = Query(...), year: int = Query(...), authorization: str = Header(...), db: Session = Depends(get_db)):
    employee_code, company_id = get_token_info(authorization)
    project = db.query(EmployeeProject).filter_by(employee_code=employee_code, company_id=company_id, month=month, year=year).first()
    return project.info if project else None
