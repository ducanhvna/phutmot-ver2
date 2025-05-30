from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.file_metadata import FileMetadata
from app.schemas.file_metadata import FileMetadataCreate, FileMetadataOut

router = APIRouter(prefix="/api/file-metadata", tags=["file-metadata"])

@router.post("/", response_model=FileMetadataOut)
def create_file_metadata(data: FileMetadataCreate, db: Session = Depends(get_db)):
    obj = FileMetadata(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/", response_model=list[FileMetadataOut])
def list_file_metadata(company_id: int = None, report_type: str = None, db: Session = Depends(get_db)):
    query = db.query(FileMetadata)
    if company_id is not None:
        query = query.filter(FileMetadata.company_id == company_id)
    if report_type is not None:
        query = query.filter(FileMetadata.report_type == report_type)
    return query.all()

@router.get("/{file_id}", response_model=FileMetadataOut)
def get_file_metadata(file_id: int, db: Session = Depends(get_db)):
    obj = db.query(FileMetadata).filter(FileMetadata.id == file_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="File metadata not found")
    return obj
