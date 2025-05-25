import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Thêm thư mục backend (chứa app/) vào sys.path để import app.* khi chạy pytest
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import os
import pytest
from app.db import Base, engine
from sqlalchemy.orm import sessionmaker
from app.models.hrms import employee as hrms_models

# Nếu dùng SQLite test DB, tự động tạo schema trước khi chạy test
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    if str(engine.url).startswith("sqlite"):
        Base.metadata.create_all(bind=engine)
    yield
    # Optionally: Xóa bảng sau test nếu cần
    # Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def clean_hrms_tables():
    """Xóa sạch dữ liệu các bảng HRMS trước mỗi test để tránh lỗi UNIQUE constraint."""
    connection = engine.connect()
    trans = connection.begin()
    for table in [
        hrms_models.EmployeeProject.__table__,
        hrms_models.EmployeeShift.__table__,
        hrms_models.EmployeeAttendance.__table__,
        hrms_models.EmployeeContract.__table__,
        hrms_models.EmployeeLogin.__table__,
        hrms_models.Employee.__table__,
    ]:
        connection.execute(table.delete())
    trans.commit()
    connection.close()
    yield

