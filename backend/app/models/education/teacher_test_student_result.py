from sqlalchemy import Column, Integer, String, Boolean
from app.db import Base

class TeacherTestStudentResult(Base):
    __tablename__ = "teacher_test_student_result"
    id = Column(Integer, primary_key=True, index=True)
    school_year = Column(Integer, comment="学年 (Năm)")
    group = Column(String, comment="組 (Nhóm)")
    number = Column(String, comment="番 (Số)")
    name = Column(String, comment="氏名 (Tên)")
    score = Column(Integer, comment="得点 (Điểm)")
    answer_status = Column(Boolean, comment="答案 (Trạng thái có/không)")
    individual_ticket_status = Column(Boolean, comment="個票 (Trạng thái có/không)")
