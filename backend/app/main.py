from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.healthcheck import HealthcheckResponse
from app.routers import auth, etl, chat
from app.routers.hrms import employee
from app.routers.hrms.buyer_auth import router
from app.routers.hrms.employee_info import employee_info_router
from app.routers.auth_user import router as auth_user_router
from app.routers.companies import router as companies_router
from app.routers.hrms import summary_report_monthly_router
from app.routers.file_metadata import router as file_metadata_router
from app.routers.education import teacher
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Cấu hình CORS
origins = [
    "https://web.hinosoft.com",
    "http://web.hinosoft.com",
    "http://localhost:3009",
    "https://localhost:3009",
    "http://localhost:3000",
    "https://localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(etl.router, prefix="/etl", tags=["etl"])
app.include_router(chat.router, tags=["chat"])
app.include_router(employee.router)
app.include_router(router)
app.include_router(employee_info_router)
app.include_router(auth_user_router)
app.include_router(companies_router)
app.include_router(summary_report_monthly_router)
app.include_router(file_metadata_router)
app.include_router(teacher.router)

@app.get("/healthcheck", response_model=HealthcheckResponse)
def healthcheck():
    return {"status": "ok"}
