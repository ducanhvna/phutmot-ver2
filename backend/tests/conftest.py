import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Thêm thư mục backend (chứa app/) vào sys.path để import app.* khi chạy pytest
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import pytest
import os
from app.db import Base, engine
from sqlalchemy.orm import sessionmaker
from app.models.hrms import employee as hrms_models

# Chỉ autouse fixture DB nếu không phải test ETL (test_etl_odoo_to_minio.py)

def is_etl_test():
    # Kiểm tra nếu pytest chỉ chạy test_etl_odoo_to_minio.py (không phải test toàn hệ thống)
    import sys
    test_files = [arg for arg in sys.argv if arg.endswith('.py') and 'test_' in arg]
    return test_files == ["tests/test_etl_odoo_to_minio.py"]

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    if is_etl_test():
        yield  # Bỏ qua setup DB nếu là test ETL
        return
    if str(engine.url).startswith("sqlite"):
        Base.metadata.create_all(bind=engine)
    yield
    # Optionally: Xóa bảng sau test nếu cần
    # Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def clean_hrms_tables():
    if is_etl_test():
        yield  # Bỏ qua clean DB nếu là test ETL
        return
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

