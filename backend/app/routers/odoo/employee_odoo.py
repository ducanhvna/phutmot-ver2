from fastapi import APIRouter, HTTPException
from app.utils.education.realtendant import get_all_employees

router = APIRouter(prefix="/api/odoo", tags=["odoo"])

@router.get("/employees")
def get_employees():
    try:
        employees = get_all_employees()
        return employees
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
