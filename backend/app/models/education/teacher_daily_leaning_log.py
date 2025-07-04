from sqlalchemy import Column, Integer, String, DateTime
from app.db import Base

class TeacherDailyLeaningLog(Base):
    __tablename__ = "teacher_daily_leaning_log"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, comment="名称 (Tên do giáo viên đặt)")
    status = Column(String, comment="Trạng thái: 実施中, 非公開, 終了")
    period_from = Column(DateTime, comment="期間 from (Thời gian bắt đầu)")
    period_to = Column(DateTime, comment="期間 to (Thời gian kết thúc)")
    subject = Column(String, comment="教科・科目 (Tên môn học)")
    subject_id = Column(Integer, comment="ID môn học")
    school_year = Column(Integer, comment="対象学年・クラス 年度")
    grade = Column(Integer, comment="対象学年・クラス 学年")
    group = Column(String, comment="Group")
    template = Column(String, comment="Template: leaningLog1, leaning_logTemplate2 hoặc None")
    creator = Column(String, comment="作成者 (Người tạo)")
    answer_request = Column(String, comment="回答依頼: Số lượng trả lời (100/200, v.v.)")
    answer_content = Column(String, comment="回答内容")
