from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.etl import ETLJob
from app.schemas.etl import ETLJobCreate, ETLJobOut
from datetime import datetime
from typing import List
import time

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
    # Giả lập ETL: lấy config, thực hiện ETL, cập nhật result
    try:
        # TODO: Thực hiện ETL thực tế ở đây
        time.sleep(2)  # Giả lập thời gian ETL
        job.status = "success"
        job.result = {"message": "ETL completed successfully"}
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
