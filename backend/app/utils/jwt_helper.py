from datetime import datetime, timedelta
from jose import jwt
from typing import Dict

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

def create_access_token(data: dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_jwt_header_for_user(user: dict) -> Dict[str, str]:
    """
    Trả về dict header Authorization: Bearer <token> cho user (dict hoặc UserOut)
    """
    token = create_access_token(user)
    return {"Authorization": f"Bearer {token}"}

# Example usage:
if __name__ == "__main__":
    user = {
        "id": 1,
        "email": "test@example.com",
        "role": "admin",
        "is_active": True,
        "username": "testuser"
    }
    headers = get_jwt_header_for_user(user)
    print(headers)
