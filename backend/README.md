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

## Tạo Superuser (quyền quản trị hệ thống)

Bạn có thể tạo superuser bằng script Python:

```sh
cd backend
python -m app.create_superuser
```

Sau đó nhập email, password, full name (nếu muốn). Ví dụ:

```text
Email: admin@yourdomain.com
Password: ********
Full name (optional): Admin Root
Superuser created: admin@yourdomain.com
```

Superuser sẽ có quyền truy cập toàn bộ hệ thống (is_superuser=True, is_staff=True, role=superadmin).

> Lưu ý: Script này chỉ cần chạy 1 lần để tạo tài khoản quản trị đầu tiên.

## Nghiệp vụ User (chuẩn Django, mở rộng)

- User có các trường:
  - email (unique, bắt buộc)
  - hashed_password (mã hóa)
  - full_name
  - is_active (kích hoạt tài khoản)
  - is_oauth, oauth_provider, oauth_id (hỗ trợ đăng nhập Google, Facebook...)
  - role (admin, employee, buyer, superadmin)
  - is_superuser (quyền full hệ thống, giống Django)
  - is_staff (quản trị nội bộ, giống Django)
  - last_login (lưu thời điểm đăng nhập cuối)
  - date_joined (ngày tạo tài khoản)
  - phone (số điện thoại, có thể dùng xác thực OTP)
  - avatar (ảnh đại diện)
  - address (địa chỉ)
  - is_verified (đã xác thực email/phone)
  - info (trường mở rộng JSON)
- Có thể mở rộng thêm các trường khác như: giới tính, ngày sinh, trạng thái xác thực 2 lớp, v.v.
- User có thể liên kết nhiều công ty (companies), nhiều subscription, nhiều payment.
- Hỗ trợ phân quyền linh hoạt: superuser, staff, admin, employee, buyer.
- Có thể tích hợp xác thực ngoài (OAuth, SSO, Google, Facebook, ...).
- Đã có script tạo superuser (`app/create_superuser.py`) và hướng dẫn sử dụng trong README.md.
- Đảm bảo bảo mật password (hash, không lưu plain text), có thể tích hợp xác thực 2 lớp (2FA) nếu cần.

## Test tự động tạo superuser

- Đã có test tự động kiểm tra nghiệp vụ tạo superuser (`tests/test_create_superuser.py`).
- Test gồm:
  - Tạo superuser mới, kiểm tra các trường quyền (`is_superuser`, `is_staff`, `role=superadmin`, `is_verified`).
  - Thử tạo superuser trùng email, kiểm tra lỗi unique.
- Test luôn xóa dữ liệu trước mỗi lần chạy để đảm bảo độc lập, dễ maintain/debug.
- Để chạy test:

```sh
pytest tests/test_create_superuser.py
```

Kết quả test sẽ báo PASSED nếu nghiệp vụ đúng chuẩn.

---

## Tổng kết

- Hệ thống đã chuẩn hóa models, API, test, migration, script tạo superuser, tài liệu chi tiết.
- Toàn bộ test tự động đã PASSED, sẵn sàng mở rộng nghiệp vụ hoặc tích hợp thực tế.
- Đảm bảo bảo mật, phân quyền, dễ maintain, CI/CD, production-ready.

---

## Triển khai production với Docker Compose (auto-migrate)

- Để đảm bảo production luôn migrate DB đúng schema mới nhất, hệ thống đã cấu hình auto-migrate trong `docker-compose.yml`:

```yaml
  fastapi:
    build: .
    ports:
      - "8979:8000"
    restart: always
    environment:
      - DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/postgres
    depends_on:
      - db
      - minio
    command: >
      sh -c "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4"
    networks:
      - backend
```

- Khi chạy `docker-compose up --build`, service FastAPI sẽ tự động migrate DB trước khi khởi động app.
- Luôn đảm bảo DB Postgres production đồng bộ với models mới nhất, không cần migrate thủ công.
- Nếu muốn test/dev với SQLite, chỉ cần chạy ngoài Docker và set lại biến môi trường `DATABASE_URL`.

## Cấu hình mail server (xác thực email)

- Để sử dụng chức năng xác thực email khi đăng ký, bạn cần cấu hình các biến môi trường sau:

| Biến môi trường | Ý nghĩa |
|-----------------|---------|
| MAIL_SERVER     | Địa chỉ SMTP server |
| MAIL_PORT       | Port SMTP (mặc định 587) |
| MAIL_USERNAME   | Tài khoản SMTP |
| MAIL_PASSWORD   | Mật khẩu SMTP |
| MAIL_FROM       | Email gửi đi |
| MAIL_USE_TLS    | true/false (mặc định true) |
| MAIL_USE_SSL    | true/false (mặc định false) |

**Ví dụ cấu hình cho Gmail:**
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_gmail@gmail.com
MAIL_PASSWORD=your_gmail_app_password
MAIL_FROM=your_gmail@gmail.com
MAIL_USE_TLS=true
MAIL_USE_SSL=false
```
> Lưu ý: Gmail yêu cầu tạo App Password (không dùng mật khẩu tài khoản Google thông thường).

**Ví dụ cấu hình cho Outlook:**
```env
MAIL_SERVER=smtp.office365.com
MAIL_PORT=587
MAIL_USERNAME=your_outlook@outlook.com
MAIL_PASSWORD=your_outlook_password
MAIL_FROM=your_outlook@outlook.com
MAIL_USE_TLS=true
MAIL_USE_SSL=false
```

- Nếu không cấu hình mail server, user sẽ được xác thực luôn khi đăng ký (auto-verified, phù hợp dev/test).
- Nếu có mail server, hệ thống sẽ gửi link xác thực email khi đăng ký.

Ví dụ cấu hình môi trường:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=yourpassword
MAIL_FROM=your@gmail.com
MAIL_USE_TLS=true
MAIL_USE_SSL=false
```

## Lưu ý môi trường TEST_SQLITE khi chạy production (Docker)

- **Chỉ sử dụng TEST_SQLITE=1 cho mục đích test, CI/CD hoặc phát triển local.**
- Khi chạy production (trong Docker Compose hoặc server thật), cần đảm bảo biến môi trường `TEST_SQLITE` **không được set** (unset hoặc không khai báo trong docker-compose).
- Nếu biến này tồn tại, backend sẽ luôn dùng SQLite thay vì Postgres, không đúng cho môi trường production thực tế.
- Docker Compose mặc định không set TEST_SQLITE, bạn chỉ cần KHÔNG thêm dòng `TEST_SQLITE=1` vào phần environment của service backend.
- Nếu đã từng set TEST_SQLITE trong môi trường host, hãy thêm dòng sau vào Dockerfile hoặc entrypoint để chắc chắn:

```sh
unset TEST_SQLITE
```

- Kiểm tra lại biến môi trường trong docker-compose.yml, Dockerfile, entrypoint.sh để đảm bảo không có TEST_SQLITE khi chạy production.

## Xoá data
### Dừng toàn bộ container
docker-compose down

### Xóa volume dữ liệu Postgres
docker volume rm backend_postgres_data

### Xóa toàn bộ file migration cũ
rm -f alembic/versions/*.py

### Khởi động lại (tự động migrate nếu entrypoint.sh hoặc command đã có alembic upgrade head)
docker-compose up --build
alembic revision --autogenerate -m "init all tables"
alembic upgrade head

## Nghiệp vụ mới & Thay đổi ETL/Báo cáo (2025-05)

### 1. Refactor ETL Odoo → MinIO
- Chuẩn hóa quy trình ETL: extract, transform, load, xuất báo cáo tổng hợp từ Odoo sang MinIO.
- Chỉ extract đúng bảng, đúng fields, ghi nhận lỗi extract (field/model không tồn tại) cho từng model, trả về extract_errors.
- Loại bỏ hoàn toàn key 'attendance', chỉ dùng 'apec_attendance_report' cho báo cáo chấm công.
- Bổ sung extract bảng `hr.attendance.trans`.
- Test ETL kiểm tra extract_errors, ghi file lỗi ra `test_result/etl_extract_errors.xlsx`.

### 2. Refactor xuất báo cáo & lưu trữ
- Mỗi loại báo cáo/mỗi công ty là 1 file riêng biệt, đặt tên chuẩn: `{company}__{report_type}__{date}.xlsx`.
- Không sinh file phòng ban, không gộp nhiều loại vào 1 file.
- Lưu metadata (json) xác định vị trí dữ liệu phòng ban trong file công ty, phục vụ API truy xuất động.
- API xuất báo cáo động: cho phép xuất/gộp báo cáo theo công ty, phòng ban, tập đoàn khi user yêu cầu.

### 3. API động xuất báo cáo (ví dụ)
- `GET /api/report/company?company_id=1&type=apec_attendance_report&date=2025-05-28` — Xuất báo cáo chấm công cho 1 công ty.
- `GET /api/report/department?company_id=1&department_id=2&type=apec_attendance_report&date=2025-05-28` — Cắt dữ liệu phòng ban từ file công ty.
- `GET /api/report/group?type=apec_attendance_report&date=2025-05-28` — Gộp nhiều công ty cho 1 loại báo cáo.

#### Ví dụ curl (PowerShell)
```powershell
# Xuất báo cáo chấm công cho 1 công ty (curl)
curl -Method GET "http://localhost:8000/api/report/company?company_id=1&type=apec_attendance_report&date=2025-05-28" -Headers @{Authorization="Bearer <token>"}

# Xuất báo cáo phòng ban (curl)
curl -Method GET "http://localhost:8000/api/report/department?company_id=1&department_id=2&type=apec_attendance_report&date=2025-05-28" -Headers @{Authorization="Bearer <token>"}

# Xuất báo cáo tập đoàn (curl)
curl -Method GET "http://localhost:8000/api/report/group?type=apec_attendance_report&date=2025-05-28" -Headers @{Authorization="Bearer <token>"}

# ---
# PowerShell chuẩn: dùng Invoke-RestMethod
# Xuất báo cáo chấm công cho 1 công ty
Invoke-RestMethod -Uri "http://localhost:8000/api/report/company?company_id=1&type=apec_attendance_report&date=2025-05-28" -Headers @{Authorization="Bearer <token>"} -Method GET -OutFile "report.xlsx"

# Xuất báo cáo phòng ban
Invoke-RestMethod -Uri "http://localhost:8000/api/report/department?company_id=1&department_id=2&type=apec_attendance_report&date=2025-05-28" -Headers @{Authorization="Bearer <token>"} -Method GET -OutFile "report_department.xlsx"

# Xuất báo cáo tập đoàn
Invoke-RestMethod -Uri "http://localhost:8000/api/report/group?type=apec_attendance_report&date=2025-05-28" -Headers @{Authorization="Bearer <token>"} -Method GET -OutFile "report_group.xlsx"
```