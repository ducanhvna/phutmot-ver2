from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.etl import ETLJob
from app.schemas.etl import ETLJobCreate, ETLJobOut
from datetime import datetime, timedelta
from typing import List
import time
from app.utils.etl_odoo_to_minio import extract_from_odoo_and_save_to_minio, extract_leaves, transform, load_to_minio
import xmlrpc.client
from app.utils.etl_odoo_to_minio import ODOO_BASE_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD
# from unities.hrms_excel_file import process_report_raw, find_couple, find_couple_out_in

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def run_etl_job(job_id: int, db: Session):
    job = db.query(ETLJob).filter(ETLJob.id == job_id).first()
    if not job:
        return
    job.status = "running"
    job.started_at = datetime.utcnow()
    db.commit()
    try:
        # Lấy ngày đầu và cuối tháng hiện tại
        now = datetime.utcnow()
        startdate = now.replace(day=1).strftime("%Y-%m-%d")
        # Lấy ngày cuối tháng
        if now.month == 12:
            next_month = now.replace(year=now.year+1, month=1, day=1)
        else:
            next_month = now.replace(month=now.month+1, day=1)
        enddate = (next_month - timedelta(days=1)).strftime("%Y-%m-%d")
        data, url = extract_from_odoo_and_save_to_minio(startdate=startdate, enddate=enddate)
        # if not data or not url:
        clean_data = transform(data, startdate=startdate, enddate=enddate)
        report_urls = load_to_minio(clean_data, f"hrms_etl_report_{datetime.now().strftime('%Y%m%d')}")
        # Tiền xử lý dữ liệu báo cáo
        # processed = process_report_raw(data)
        # couple = find_couple(processed)
        # couple_out_in = find_couple_out_in(processed)
        job.status = "success"
        job.result = {
            "message": "ETL completed successfully",
            "url": url,
            "report_urls": report_urls,
            # "processed_preview": str(processed)[:500],
            # "couple_preview": str(couple)[:500],
            # "couple_out_in_preview": str(couple_out_in)[:500]
        }
    except Exception as e:
        job.status = "failed"
        job.result = {"error": str(e)}
    finally:
        job.finished_at = datetime.utcnow()
        db.commit()

@router.post("/etl-jobs/", response_model=ETLJobOut)
def create_etl_job(job: ETLJobCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_job = ETLJob(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    background_tasks.add_task(run_etl_job, db_job.id, db)
    return db_job

@router.get("/etl-jobs/", response_model=List[ETLJobOut])
def list_etl_jobs(db: Session = Depends(get_db)):
    return db.query(ETLJob).all()

@router.get("/etl-jobs/{job_id}", response_model=ETLJobOut)
def get_etl_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(ETLJob).filter(ETLJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/hr-leaves/")
def get_hr_leaves(
    startdate: str = Query(None, description="YYYY-MM-DD"),
    enddate: str = Query(None, description="YYYY-MM-DD")
):
    # Kết nối Odoo
    common = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/object")
    leaves = extract_leaves(models, uid, limit=1000, offset=0, startdate=startdate, enddate=enddate)
    return {"leaves": leaves}
