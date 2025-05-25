import os
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.etl import ETLJob
from app.routers.etl import run_etl_job
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

# Cho phép override DB cho test: nếu TEST_SQLITE=1 thì dùng sqlite
if os.getenv("TEST_SQLITE") == "1":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine("sqlite:///test.db", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
