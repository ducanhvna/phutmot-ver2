from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.education.teacher_test_result_summary import TeacherTestResultSummary
from app.models.education.teacher_test_student_result import TeacherTestStudentResult
from app.models.education.teacher_daily_leaning_log import TeacherDailyLeaningLog
from typing import List
from datetime import datetime
from pydantic import BaseModel
from app.utils.jwt_helper import get_current_user

router = APIRouter(prefix="/api/education/teacher", tags=["education_teacher"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

class TeacherTestResultSummaryBase(BaseModel):
    teacher_id: int
    teacher_name: str
    update_datetime: datetime = None
    test: str = None
    subject: str = None
    implementation_date: datetime = None
    answer: str = None
    answer_status: bool = None
    problem_attribute: str = None
    problem_attribute_status: bool = None
    individual_ticket: str = None
    individual_ticket_status: bool = None
    review: str = None
    review_setting_status: bool = None
    review_response: str = None
    review_response_unanswered: str = None
    lrt: str = None
    lrt_status: bool = None
    realtendant_tool: str = None
    realtendant_tool_status: bool = None
    # Bổ sung các trường còn thiếu
    school_year: int = None  # 学年 (Năm)
    school_name: str = None  # Tên trường học
    school_id: int = None    # ID trường học
    average_score: int = None  # 得点 (Điểm trung bình)
    correct_answer_rate_total: str = None  # 正答率（％）- 全体
    correct_answer_rate_knowledge: str = None  # 正答率（％）- 知識・技能
    correct_answer_rate_thinking: str = None  # 正答率（％）- 思考・判断・表現
    careless_mistake_count: int = None  # ケアレスミスかも (Số câu có thể là lỗi bất cẩn)
    deviation_value: str = None  # 偏差値
    understanding_rank: str = None  # 理解度ランク

class TeacherTestResultSummaryCreate(TeacherTestResultSummaryBase):
    pass

class TeacherTestResultSummaryUpdate(TeacherTestResultSummaryBase):
    pass

class TeacherTestResultSummaryOut(TeacherTestResultSummaryBase):
    id: int
    class Config:
        orm_mode = True

class TeacherTestResultSummaryListOut(BaseModel):
    id: int
    teacher_id: int
    teacher_name: str
    update_datetime: datetime = None
    test: str = None
    subject: str = None
    implementation_date: datetime = None
    answer: str = None
    answer_status: bool = None
    problem_attribute: str = None
    problem_attribute_status: bool = None
    individual_ticket: str = None
    individual_ticket_status: bool = None
    review: str = None
    review_setting_status: bool = None
    review_response: str = None
    review_response_unanswered: str = None
    lrt: str = None
    lrt_status: bool = None
    realtendant_tool: str = None
    realtendant_tool_status: bool = None
    school_year: int = None
    school_name: str = None
    school_id: int = None
    average_score: int = None
    class Config:
        orm_mode = True

@router.get("/test/", response_model=List[TeacherTestResultSummaryListOut])
def list_teacher_test_result_summaries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(TeacherTestResultSummary).offset(skip).limit(limit).all()

@router.get("/test/{summary_id}", response_model=TeacherTestResultSummaryOut)
def get_teacher_test_result_summary(summary_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    summary = db.query(TeacherTestResultSummary).filter(TeacherTestResultSummary.id == summary_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary

@router.post("/test/", response_model=TeacherTestResultSummaryOut)
def create_teacher_test_result_summary(summary: TeacherTestResultSummaryCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_summary = TeacherTestResultSummary(**summary.dict())
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)
    return db_summary

@router.put("/test/{summary_id}", response_model=TeacherTestResultSummaryOut)
def update_teacher_test_result_summary(summary_id: int, summary: TeacherTestResultSummaryUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_summary = db.query(TeacherTestResultSummary).filter(TeacherTestResultSummary.id == summary_id).first()
    if not db_summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    for key, value in summary.dict(exclude_unset=True).items():
        setattr(db_summary, key, value)
    db.commit()
    db.refresh(db_summary)
    return db_summary

@router.delete("/test/{summary_id}")
def delete_teacher_test_result_summary(summary_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_summary = db.query(TeacherTestResultSummary).filter(TeacherTestResultSummary.id == summary_id).first()
    if not db_summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    db.delete(db_summary)
    db.commit()
    return {"ok": True, "deleted_id": summary_id}

class TeacherTestStudentResultBase(BaseModel):
    school_year: int
    group: str
    number: str
    name: str
    score: int
    answer_status: bool = None
    individual_ticket_status: bool = None

class TeacherTestStudentResultCreate(TeacherTestStudentResultBase):
    pass

class TeacherTestStudentResultUpdate(TeacherTestStudentResultBase):
    pass

class TeacherTestStudentResultOut(TeacherTestStudentResultBase):
    id: int
    class Config:
        orm_mode = True

@router.get("/test-student/", response_model=List[TeacherTestStudentResultOut])
def list_teacher_test_student_results(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(TeacherTestStudentResult).offset(skip).limit(limit).all()

@router.get("/test-student/{item_id}", response_model=TeacherTestStudentResultOut)
def get_teacher_test_student_result(item_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    item = db.query(TeacherTestStudentResult).filter(TeacherTestStudentResult.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/test-student/", response_model=TeacherTestStudentResultOut)
def create_teacher_test_student_result(item: TeacherTestStudentResultCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_item = TeacherTestStudentResult(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/test-student/{item_id}", response_model=TeacherTestStudentResultOut)
def update_teacher_test_student_result(item_id: int, item: TeacherTestStudentResultUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_item = db.query(TeacherTestStudentResult).filter(TeacherTestStudentResult.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in item.dict(exclude_unset=True).items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/test-student/{item_id}")
def delete_teacher_test_student_result(item_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_item = db.query(TeacherTestStudentResult).filter(TeacherTestStudentResult.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"ok": True, "deleted_id": item_id}

class TeacherDailyLeaningLogBase(BaseModel):
    name: str
    status: str
    period_from: datetime = None
    period_to: datetime = None
    subject: str = None
    subject_id: int = None
    school_year: int = None
    grade: int = None
    group: str = None
    template: str = None
    creator: str = None
    answer_request: str = None
    answer_content: str = None

class TeacherDailyLeaningLogCreate(BaseModel):
    name: str
    status: str
    period_from: datetime = None
    period_to: datetime = None
    subject: str = None
    subject_id: int = None
    school_year: int = None
    grade: int = None
    group: str = None
    template: str = None
    creator: str = None
    answer_request: str = None
    answer_content: str = None

class TeacherDailyLeaningLogUpdate(TeacherDailyLeaningLogBase):
    pass

class TeacherDailyLeaningLogOut(TeacherDailyLeaningLogBase):
    id: int
    class Config:
        orm_mode = True

@router.get("/daily-leaning-log/", response_model=List[TeacherDailyLeaningLogOut])
def list_teacher_daily_leaning_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(TeacherDailyLeaningLog).offset(skip).limit(limit).all()

@router.get("/daily-leaning-log/{log_id}", response_model=TeacherDailyLeaningLogOut)
def get_teacher_daily_leaning_log(log_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    log = db.query(TeacherDailyLeaningLog).filter(TeacherDailyLeaningLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log

@router.post("/daily-leaning-log/", response_model=TeacherDailyLeaningLogOut)
def create_teacher_daily_leaning_log(log: TeacherDailyLeaningLogCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_log = TeacherDailyLeaningLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@router.put("/daily-leaning-log/{log_id}", response_model=TeacherDailyLeaningLogOut)
def update_teacher_daily_leaning_log(log_id: int, log: TeacherDailyLeaningLogUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_log = db.query(TeacherDailyLeaningLog).filter(TeacherDailyLeaningLog.id == log_id).first()
    if not db_log:
        raise HTTPException(status_code=404, detail="Log not found")
    for key, value in log.dict(exclude_unset=True).items():
        setattr(db_log, key, value)
    db.commit()
    db.refresh(db_log)
    return db_log

@router.delete("/daily-leaning-log/{log_id}")
def delete_teacher_daily_leaning_log(log_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_log = db.query(TeacherDailyLeaningLog).filter(TeacherDailyLeaningLog.id == log_id).first()
    if not db_log:
        raise HTTPException(status_code=404, detail="Log not found")
    db.delete(db_log)
    db.commit()
    return {"ok": True, "deleted_id": log_id}
