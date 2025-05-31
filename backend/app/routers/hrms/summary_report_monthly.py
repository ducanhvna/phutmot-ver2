from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, cast, String
from fastapi.responses import JSONResponse

from app.db import get_db
from app.models.hrms.summary_report_monthly import SummaryReportMonthlyReport
from app.schemas.hrms.summary_report_monthly import (
    SummaryReportMonthlyReportCreate, SummaryReportMonthlyReportOut
)

router = APIRouter(prefix="/api/hrms", tags=["hrms"])

@router.post("/summary-report-monthly", response_model=SummaryReportMonthlyReportOut)
def create_summary_report_monthly(data: SummaryReportMonthlyReportCreate, db: Session = Depends(get_db)):
    obj = SummaryReportMonthlyReport(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/summary-report-monthly")
def list_summary_report_monthly(
    page: int = 1,
    pagesize: int = 20,
    employee_code: str = None,
    search: str = None,
    month: int = None,
    year: int = None,
    db: Session = Depends(get_db)
):
    query = db.query(SummaryReportMonthlyReport)
    if employee_code:
        query = query.filter(SummaryReportMonthlyReport.employee_code == employee_code)
    if month is not None:
        query = query.filter(SummaryReportMonthlyReport.month == month)
    if year is not None:
        query = query.filter(SummaryReportMonthlyReport.year == year)
    if search:
        query = query.filter(
            or_(
                cast(SummaryReportMonthlyReport.info, String).ilike(f"%{search}%"),
                SummaryReportMonthlyReport.employee_code.ilike(f"%{search}%")
            )
        )
    total = query.count()
    items = query.offset((page-1)*pagesize).limit(pagesize).all()
    return {
        "total": total,
        "page": page,
        "pagesize": pagesize,
        "items": items
    }

@router.get("/summary-report-monthly/{report_id}", response_model=SummaryReportMonthlyReportOut)
def get_summary_report_monthly(report_id: int, db: Session = Depends(get_db)):
    obj = db.query(SummaryReportMonthlyReport).filter(SummaryReportMonthlyReport.id == report_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Report not found")
    return obj

@router.put("/summary-report-monthly/{report_id}", response_model=SummaryReportMonthlyReportOut)
def update_summary_report_monthly(report_id: int, data: SummaryReportMonthlyReportCreate, db: Session = Depends(get_db)):
    obj = db.query(SummaryReportMonthlyReport).filter(SummaryReportMonthlyReport.id == report_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Report not found")
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/summary-report-monthly/{report_id}")
def delete_summary_report_monthly(report_id: int, db: Session = Depends(get_db)):
    obj = db.query(SummaryReportMonthlyReport).filter(SummaryReportMonthlyReport.id == report_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Report not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
