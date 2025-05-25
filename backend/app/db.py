from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Ưu tiên TEST_SQLITE=1 để ép dùng SQLite cho toàn bộ hệ thống test
if os.getenv("TEST_SQLITE") == "1":
    DATABASE_URL = "sqlite:///./test.db"
    connect_args = {"check_same_thread": False}
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
