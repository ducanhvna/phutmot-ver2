# Đã chuyển models và schemas sang các subfolder app/models và app/schemas.
# Nếu có model/schema cụ thể, hãy tạo file riêng trong các thư mục này.

# Định nghĩa các schema (Pydantic models) dùng cho API
from pydantic import BaseModel

class HealthcheckResponse(BaseModel):
    status: str
