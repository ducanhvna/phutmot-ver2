from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def create_buyer_token(employee_code: str, company_id: int, expires_delta: int = 3600):
    expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
    to_encode = {
        "employee_code": employee_code,
        "company_id": company_id,
        "role": "buyer",
        "exp": expire
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_buyer_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("role") != "buyer":
            return None
        return payload
    except JWTError:
        return None
