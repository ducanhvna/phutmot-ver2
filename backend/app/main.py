from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.healthcheck import HealthcheckResponse
from app.routers import auth, etl

app = FastAPI()

# Cấu hình CORS
origins = [
    "https://web.hinosoft.com",
    "http://web.hinosoft.com",
    "http://localhost:3009",
    "https://localhost:3009"
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

@app.get("/healthcheck", response_model=HealthcheckResponse)
def healthcheck():
    return {"status": "ok"}
