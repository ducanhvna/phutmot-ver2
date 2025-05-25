from fastapi import APIRouter, HTTPException, Depends, Query, Header
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.hrms.employee import Employee, EmployeeLogin, EmployeeContract, EmployeeAttendance, EmployeeShift, EmployeeProject
from app.utils.buyer_jwt import create_buyer_token, decode_buyer_token

router = APIRouter(prefix="/api/hrms", tags=["hrms-employee-auth"])

@router.post("/employee-login/auth")
def employee_login_auth(
    employee_code: str = Query(...),
    company_id: int = Query(...),
    password: str = Query(...),
    db: Session = Depends(get_db)
):
    login = db.query(EmployeeLogin).filter_by(employee_code=employee_code, company_id=company_id).first()
    if not login or not login.info or login.info.get("password") != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_buyer_token(employee_code, company_id)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/employee-login/me")
def employee_login_me(token: str = Query(...), db: Session = Depends(get_db)):
    buyer = decode_buyer_token(token)
    if not buyer:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    login = db.query(EmployeeLogin).filter_by(
        employee_code=buyer["employee_code"], company_id=buyer["company_id"]
    ).first()
    return {
        "employee_code": buyer["employee_code"],
        "company_id": buyer["company_id"],
        "info": login.info if login else None
    }

@router.get("/employee-login/info")
def get_employee_all_info(
    month: int = Query(...),
    year: int = Query(...),
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ", 1)[1]
    buyer = decode_buyer_token(token)
    if not buyer:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    employee_code = buyer["employee_code"]
    company_id = buyer["company_id"]
    # Lấy thông tin từng bảng
    employee = db.query(Employee).filter_by(employee_code=employee_code, company_id=company_id).first()
    login = db.query(EmployeeLogin).filter_by(employee_code=employee_code, company_id=company_id).first()
    contract = db.query(EmployeeContract).filter_by(employee_code=employee_code, company_id=company_id, month=month, year=year).first()
    attendance = db.query(EmployeeAttendance).filter_by(employee_code=employee_code, company_id=company_id, month=month, year=year).first()
    shift = db.query(EmployeeShift).filter_by(employee_code=employee_code, company_id=company_id, month=month, year=year).first()
    project = db.query(EmployeeProject).filter_by(employee_code=employee_code, company_id=company_id, month=month, year=year).first()
    return {
        "employee": employee.info if employee else None,
        "login": login.info if login else None,
        "contract": contract.info if contract else None,
        "attendance": attendance.info if attendance else None,
        "shift": shift.info if shift else None,
        "project": project.info if project else None
    }
