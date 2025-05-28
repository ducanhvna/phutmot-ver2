from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from fastapi import WebSocket
from app.schemas.core import UserOut
from typing import Optional

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    # Sửa lỗi: expires_delta có thể là timedelta hoặc int (phút)
    if isinstance(expires_delta, timedelta):
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception as e:
        raise e

async def get_current_user_from_ws(websocket: WebSocket) -> Optional[UserOut]:
    token = None
    # Lấy token từ query param hoặc header (tùy frontend gửi)
    if "token" in websocket.query_params:
        token = websocket.query_params["token"]
    elif "authorization" in websocket.headers:
        auth_header = websocket.headers["authorization"]
        if auth_header.lower().startswith("bearer "):
            token = auth_header[7:]
    if not token:
        await websocket.close(code=1008)
        return None
    try:
        payload = verify_jwt_token(token)
        return UserOut(**payload)
    except Exception:
        await websocket.close(code=1008)
        return None
