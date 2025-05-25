from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.etl import ETLJob
from app.routers.etl import run_etl_job
from datetime import datetime

scheduler = BackgroundScheduler()

def schedule_pending_etl_jobs():
    db: Session = SessionLocal()
    try:
        jobs = db.query(ETLJob).filter(ETLJob.status == "pending", ETLJob.is_active == True).all()
        for job in jobs:
            run_etl_job(job.id, db)
    finally:
        db.close()

scheduler.add_job(schedule_pending_etl_jobs, "interval", minutes=20)
scheduler.start()
