# FastAPI Multiprocessor Project

This project is a minimal FastAPI app ready for multiprocessor (multi-core) serving using Uvicorn.

## Development

```sh
uvicorn main:app --reload
```

## Production (multi-core)

```sh
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Kiến trúc hệ thống

- **Backend**: FastAPI đa lĩnh vực (giáo dục, y tế, nhân sự), tổ chức chuẩn hóa theo domain (education, healthcare, hrms), hỗ trợ đa tiến trình (uvicorn --workers=N), phân quyền (admin, employee, buyer, superadmin), JWT, OAuth, ETL định kỳ, báo cáo, chat realtime (WebSocket), lưu trữ file MinIO, migration tự động (Alembic), test tự động (pytest), Docker Compose đa service (Postgres, MinIO, FastAPI), CORS frontend.

- **Thư mục chính**:
  - `app/models/`: Models SQLAlchemy, chia theo domain, hỗ trợ trường info mở rộng (JSONB)
  - `app/schemas/`: Pydantic schemas, chia theo domain
  - `app/routers/`: Routers API, chia theo domain, gồm auth, etl, chat, healthcheck
  - `app/utils/`: Tiện ích auth, ETL scheduler, báo cáo, chat
  - `tests/`: Test tự động pytest
  - `Dockerfile`, `docker-compose.yml`, `entrypoint.sh`: Triển khai đa service, chờ DB, mount volume
  - `alembic.ini`: Migration DB

## Nghiệp vụ chính

- Đăng ký/đăng nhập (truyền thống, JWT, hỗ trợ OAuth Google/Facebook)
- Phân quyền người dùng: admin, employee, buyer, superadmin
- Quản lý công ty, dịch vụ (5 plan), đăng ký dịch vụ, thanh toán (online/offline)
- Quản lý ETL định kỳ (APScheduler), sinh báo cáo Excel/CSV (pandas, openpyxl, xlrd)
- Lưu trữ file với MinIO (chuẩn S3)
- Chat realtime đa user (WebSocket, lưu lịch sử tạm thời, phân quyền chat)
- Tổ chức code chuẩn, hỗ trợ migration tự động, test, CI/CD, production

## API chi tiết

### Auth

- `POST /auth/register` — Đăng ký tài khoản
- `POST /auth/login` — Đăng nhập truyền thống (JWT)
- `POST /auth/oauth/google` — Đăng nhập Google (nếu tích hợp)
- `POST /auth/oauth/facebook` — Đăng nhập Facebook (nếu tích hợp)

### Company/Service/Subscription

- `GET /company/` — Danh sách công ty
- `POST /company/` — Tạo công ty
- `GET /service/` — Danh sách dịch vụ/plan
- `POST /subscription/` — Đăng ký dịch vụ
- `GET /subscription/` — Lịch sử đăng ký dịch vụ

### Payment

- `POST /payment/` — Tạo thanh toán (online/offline)
- `GET /payment/` — Lịch sử thanh toán

### ETL & Báo cáo

- `POST /etl/job` — Tạo job ETL
- `GET /etl/job` — Danh sách job ETL
- `GET /etl/result/{job_id}` — Kết quả ETL
- `POST /etl/report` — Sinh báo cáo Excel/CSV

### File/MinIO

- `POST /file/upload` — Upload file lên MinIO
- `GET /file/download/{file_id}` — Download file từ MinIO

### Chat (WebSocket)

- `ws://<host>:8000/ws/chat?token=...` — Kết nối chat realtime, xác thực JWT, phân quyền, nhận/gửi tin nhắn, nhận lịch sử

### Healthcheck

- `GET /health` — Kiểm tra trạng thái hệ thống

## Hướng dẫn chạy

1. Cài Docker, docker-compose
2. `docker-compose up --build`
3. Truy cập API docs: `http://localhost:8000/docs`
4. Chạy test: `pytest tests`

## Ghi chú

- Để chạy production đa core: `uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4`
- Có thể mở rộng thêm domain, tích hợp OAuth, lưu lịch sử chat vào DB, CI/CD, ...

## Employee (Khách hàng/Người mua) Login qua EmployeeLogin

- Cho phép khách hàng của công ty (employee/buyer) đăng nhập và lấy thông tin cá nhân chỉ dựa vào bảng `EmployeeLogin` (không cần tạo user ở bảng User chính).
- Khi đăng nhập, API kiểm tra employee_code, company_id, password trong bảng `hrms_employee_login`.
- Nếu hợp lệ, sinh JWT token chứa thông tin employee (employee_code, company_id, role=buyer).
- Các API employee chỉ cần xác thực JWT này, không cần xác thực qua bảng User.
- Có thể forward xác thực sang service auth khác nếu muốn (dễ tích hợp SSO, OAuth, ...).

### API Employee Login

- `POST /api/hrms/employee-login/auth` — Đăng nhập employee (buyer)
- `GET /api/hrms/employee-login/me` — Lấy thông tin employee (buyer) từ JWT

### Test tự động employee-login

- Đã có test tự động cho toàn bộ API employee-login (`tests/test_hrms_buyer_auth.py`).
- Test sẽ tạo employee, đăng nhập, lấy thông tin employee-login/me, kiểm tra unique, phân quyền, và xóa dữ liệu trước mỗi test.


## HRMS (Quản lý nhân sự)

- Quản lý nhân sự (HRMS) gồm các bảng:
    - `Employee`: Thông tin nhân sự (employee_code, name, company_id, info...)
    - `EmployeeLogin`: Đăng nhập nhân sự (employee_code, company_id, password)
    - `EmployeeContract`: Hợp đồng lao động (employee_code, company_id, info, thời hạn...)
    - `EmployeeAttendance`: Chấm công (employee_code, company_id, ngày, trạng thái, info...)
    - `EmployeeShift`: Ca làm việc (employee_code, company_id, ngày, ca, info...)
    - `EmployeeProject`: Quản lý dự án nhân sự (employee_code, company_id, tháng, năm, info dạng JSONB)
- Các bảng đều có index cho các trường thường truy vấn, dùng JSON/JSONB cho info mở rộng.
- API CRUD cho từng bảng, prefix `/api/hrms`, xác thực JWT, phân quyền theo vai trò (admin, employee, buyer).
- Đảm bảo unique theo employee_code, tháng, năm, company_id cho các bảng liên quan (ví dụ: EmployeeProject).
- Test tự động cho toàn bộ API HRMS (`tests/test_hrms_employee.py`), bao gồm tạo, sửa, xóa, truy vấn, kiểm tra unique, phân quyền.
- Khi test, dữ liệu HRMS được xóa trước mỗi test để tránh lỗi unique constraint.
- Có thể mở rộng thêm trường info, tích hợp xác thực ngoài, hoặc đồng bộ dữ liệu với hệ thống HR khác.

### API HRMS

- `POST /api/hrms/employee` — Tạo nhân sự
- `GET /api/hrms/employee` — Danh sách nhân sự
- `PUT /api/hrms/employee/{id}` — Sửa thông tin nhân sự
- `DELETE /api/hrms/employee/{id}` — Xóa nhân sự
- `POST /api/hrms/employee-login` — Tạo thông tin đăng nhập nhân sự
- `GET /api/hrms/employee-login` — Danh sách đăng nhập nhân sự
- ... (tương tự cho contract, attendance, shift, project)


### Test tự động

- Đã có test tự động cho toàn bộ API HRMS (`tests/test_hrms_employee.py`).
- Test sẽ tạo nhân sự, đăng nhập, hợp đồng, chấm công, ca làm việc, dự án, kiểm tra unique, phân quyền, và xóa dữ liệu trước mỗi test.


### Lưu ý kỹ thuật

- Sử dụng JSON/JSONB cho info mở rộng, dễ tích hợp các trường động.
- Index các trường thường truy vấn để tối ưu hiệu năng.
- Dùng datetime timezone-aware (UTC) cho các trường thời gian.
- Có thể tích hợp xác thực ngoài hoặc forward auth nếu cần.
