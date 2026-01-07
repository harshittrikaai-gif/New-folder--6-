"""File upload endpoints for RAG documents."""
import os
import uuid
import aiofiles
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from ..engine.rag import RAGEngine

router = APIRouter(prefix="/files", tags=["files"])

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class UploadedFile(BaseModel):
    """Uploaded file response."""
    id: str
    filename: str
    content_type: str
    size: int
    indexed: bool = False


class FileList(BaseModel):
    """List of uploaded files."""
    files: List[UploadedFile]


# In-memory file tracking
uploaded_files: dict = {}


@router.post("/upload", response_model=UploadedFile)
async def upload_file(file: UploadFile = File(...)):
    """Upload a file for RAG indexing."""
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    
    # Save file
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)
    
    # Index in RAG
    rag_engine = RAGEngine()
    try:
        await rag_engine.index_document(file_path, file.filename)
        indexed = True
    except Exception:
        indexed = False
    
    uploaded_file = UploadedFile(
        id=file_id,
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        size=len(content),
        indexed=indexed
    )
    uploaded_files[file_id] = {
        "info": uploaded_file,
        "path": file_path
    }
    
    return uploaded_file


@router.get("/", response_model=FileList)
async def list_files():
    """List all uploaded files."""
    return FileList(files=[f["info"] for f in uploaded_files.values()])


@router.delete("/{file_id}")
async def delete_file(file_id: str):
    """Delete an uploaded file."""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_data = uploaded_files[file_id]
    
    # Remove from filesystem
    if os.path.exists(file_data["path"]):
        os.remove(file_data["path"])
    
    # Remove from RAG index
    rag_engine = RAGEngine()
    await rag_engine.remove_document(file_id)
    
    del uploaded_files[file_id]
    return {"status": "deleted"}
