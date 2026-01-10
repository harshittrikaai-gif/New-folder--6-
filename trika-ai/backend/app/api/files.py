from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import os
import uuid
import aiofiles

from ..db.database import get_db
from ..db.models import Document as DocumentDB
from ..engine.rag import RAGEngine

router = APIRouter(prefix="/files", tags=["files"])

UPLOAD_DIR = "uploads" # Store locally in the project dir
os.makedirs(UPLOAD_DIR, exist_ok=True)


class UploadedFile(BaseModel):
    """Uploaded file response."""
    id: str
    filename: str
    content_type: str
    size: int
    indexed: bool = False
    created_at: str = ""

    class Config:
        from_attributes = True


class FileList(BaseModel):
    """List of uploaded files."""
    files: List[UploadedFile]


@router.post("/upload", response_model=UploadedFile)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a file for RAG indexing."""
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    
    # Save file
    content = await file.read()
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)
    
    # Index in RAG
    rag_engine = RAGEngine()
    indexed = 0
    try:
        await rag_engine.index_document(file_path, file.filename)
        indexed = 1
    except Exception as e:
        print(f"Indexing error: {e}")
        indexed = 0
    
    # Save to DB
    db_file = DocumentDB(
        id=file_id,
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        size=len(content),
        path=file_path,
        indexed=indexed
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    return UploadedFile(
        id=db_file.id,
        filename=db_file.filename,
        content_type=db_file.content_type,
        size=db_file.size,
        indexed=bool(db_file.indexed),
        created_at=str(db_file.created_at)
    )


@router.get("/", response_model=FileList)
async def list_files(db: Session = Depends(get_db)):
    """List all uploaded files."""
    files = db.query(DocumentDB).all()
    return FileList(files=[
        UploadedFile(
            id=f.id,
            filename=f.filename,
            content_type=f.content_type,
            size=f.size,
            indexed=bool(f.indexed),
            created_at=str(f.created_at)
        ) for f in files
    ])


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    db: Session = Depends(get_db)
):
    """Delete an uploaded file."""
    db_file = db.query(DocumentDB).filter(DocumentDB.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Remove from filesystem
    if os.path.exists(db_file.path):
        os.remove(db_file.path)
    
    # Remove from RAG index
    try:
        rag_engine = RAGEngine()
        await rag_engine.remove_document(file_id)
    except Exception:
        pass # Best effort cleanup
    
    db.delete(db_file)
    db.commit()
    
    return {"status": "deleted"}
