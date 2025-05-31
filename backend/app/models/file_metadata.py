from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.sql import func
from app.db import Base
from sqlalchemy.dialects.postgresql import insert
from app.db import SessionLocal

class FileMetadata(Base):
    __tablename__ = "file_metadata"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)
    report_type = Column(String, index=True)
    file_url = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(String)
    info = Column(JSON, default={})
    __table_args__ = (UniqueConstraint("company_id", "report_type", "file_name", name="uq_file_metadata"),)

def save_file_metadata_list(links):
    """
    Lưu metadata file vào bảng FileMetadata, upsert theo (company_id, report_type, file_name).
    links: dict[file_name, url]
    """
    session = SessionLocal()
    try:
        for file_name, url in links.items():
            # Parse company_id và report_type từ file_name nếu có thể
            parts = file_name.split("__")
            company_id = None
            report_type = None
            if len(parts) >= 2:
                try:
                    company_id = int(parts[0]) if parts[0].isdigit() else None
                except Exception:
                    company_id = None
                report_type = parts[1]
            stmt = insert(FileMetadata).values(
                company_id=company_id,
                report_type=report_type,
                file_url=url,
                file_name=file_name,
                created_by="etl",
                info={}
            ).on_conflict_do_update(
                index_elements=[FileMetadata.company_id, FileMetadata.report_type, FileMetadata.file_name],
                set_={
                    "file_url": url,
                    "created_by": "etl",
                    "info": {},
                }
            )
            session.execute(stmt)
        session.commit()
    except Exception as ex:
        print(f"[ETL] Save file metadata to DB failed: {ex}")
    finally:
        session.close()
