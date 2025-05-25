from app.db import SessionLocal
from app.models.core import User, UserRoleEnum
from passlib.hash import bcrypt

def create_superuser(email, password, full_name=None):
    db = SessionLocal()
    if db.query(User).filter_by(email=email).first():
        print("User already exists!")
        return
    user = User(
        email=email,
        hashed_password=bcrypt.hash(password),
        full_name=full_name,
        is_active=True,
        is_superuser=True,
        is_staff=True,
        role=UserRoleEnum.SUPERADMIN,
        is_verified=True
    )
    db.add(user)
    db.commit()
    print("Superuser created:", email)

if __name__ == "__main__":
    import getpass
    email = input("Email: ")
    password = getpass.getpass("Password: ")
    full_name = input("Full name (optional): ") or None
    create_superuser(email, password, full_name)
