from .db import Base
from sqlalchemy import Column, Integer, String

# Đã chuyển models và schemas sang các subfolder app/models và app/schemas.
# Nếu có model/schema cụ thể, hãy tạo file riêng trong các thư mục này.

class ExampleModel(Base):
    __tablename__ = "example"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
