import os
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.etl import ETLJob
from app.routers.etl import run_etl_job
from datetime import datetime
from celery import Celery
from celery.schedules import crontab

# Cho phép override DB cho test: nếu TEST_SQLITE=1 thì dùng sqlite
if os.getenv("TEST_SQLITE") == "1":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine("sqlite:///test.db", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Khởi tạo Celery
celery_app = Celery(
    "etl_tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0"),
)

def ensure_initial_etl_job(db: Session):
    """Đảm bảo luôn có ít nhất 1 job ETL pending, active trong DB, nếu chưa có thì tạo job mẫu."""
    from app.models.etl import ETLJob
    from app.models.core import Company
    job = db.query(ETLJob).filter(
        ETLJob.status == "pending",
        ETLJob.is_active == True
    ).first()
    if not job:
        # Lấy company đầu tiên làm mặc định nếu chưa có
        company = db.query(Company).first()
        if not company:
            raise Exception("No company found in database")
        job = ETLJob(
            company_id=company.id,
            name="ETL Job Auto",
            status="pending",
            is_active=True
        )
        db.add(job)
        db.commit()

@celery_app.task
def schedule_pending_etl_jobs():
    db: Session = SessionLocal()
    try:
        ensure_initial_etl_job(db)
        jobs = db.query(ETLJob).filter(ETLJob.status == "pending", ETLJob.is_active == True).all()
        for job in jobs:
            run_etl_job(job.id, db)
    finally:
        db.close()

# Đăng ký task chạy mỗi 3 phút
celery_app.conf.beat_schedule = {
    'run-etl-every-9-minutes': {
        'task': 'app.utils.etl_scheduler.schedule_pending_etl_jobs',
        'schedule': crontab(minute='*/9'),
    },
}
