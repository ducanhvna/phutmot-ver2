from fastapi import APIRouter, HTTPException
from app.utils.education.realtendant import get_all_employees, get_employee_by_id

router = APIRouter(prefix="/api/odoo", tags=["odoo"])

@router.get("/employees")
def get_employees():
    try:
        employees = get_all_employees()
        return employees
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/employees/{emp_id}")
def get_employee_detail(emp_id: int):
    try:
        employee = get_employee_by_id(emp_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        return employee
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
