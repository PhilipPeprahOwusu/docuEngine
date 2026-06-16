"""Document Routes"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.document import Document
from app.models.user import User
from app.core.security import oauth2_scheme, decode_access_token
from app.core.config import settings
from app.services.storage_service import StorageService
from datetime import datetime
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_current_user_from_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get current user from JWT token"""
    token_data = decode_access_token(token)
    if not token_data or not token_data.sub:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    user = db.query(User).filter(User.user_id == token_data.sub).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(default="contract"),
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Upload a new document to cloud storage"""
    try:
        logger.info(f"Uploading document: {file.filename} for user: {current_user.user_id}")

        # Initialize storage service
        storage = StorageService(provider=settings.STORAGE_PROVIDER)

        # Upload file to cloud storage
        storage_key, file_content = await storage.upload_file(
            file=file,
            org_id=str(current_user.org_id)
        )

        # Extract text content for indexing (for text files)
        content_preview = None
        try:
            content_preview = file_content.decode('utf-8')[:10000]  # Store first 10KB for preview
        except UnicodeDecodeError:
            # Binary file - will be processed later by document parsing service
            content_preview = f"[Binary file: {file.filename}]"

        # Create document record
        new_document = Document(
            document_id=uuid.uuid4(),
            org_id=current_user.org_id,
            filename=file.filename,
            file_size_bytes=len(file_content),
            content=content_preview,  # Store preview or binary placeholder
            document_type=document_type,
            created_by=current_user.user_id,
            parties=[],
            s3_key=storage_key,  # Store cloud storage key
            status="pending"
        )

        db.add(new_document)
        db.commit()
        db.refresh(new_document)

        logger.info(f"Document uploaded successfully: {new_document.document_id}")

        return {
            "id": str(new_document.document_id),
            "filename": new_document.filename,
            "document_type": new_document.document_type,
            "file_size": new_document.file_size_bytes,
            "created_at": new_document.created_at.isoformat(),
            "status": "uploaded",
            "storage_key": storage_key
        }

    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")


@router.get("/")
async def list_documents(
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """List all documents for the current user's organization"""
    documents = db.query(Document).filter(
        Document.org_id == current_user.org_id
    ).order_by(Document.created_at.desc()).offset(skip).limit(limit).all()

    return [{
        "id": str(doc.document_id),
        "filename": doc.filename,
        "document_type": doc.document_type,
        "file_size": doc.file_size_bytes,
        "created_at": doc.created_at.isoformat(),
        "creator_id": str(doc.created_by),
        "parties": doc.parties or []
    } for doc in documents]


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Get a specific document"""
    document = db.query(Document).filter(
        Document.document_id == document_id,
        Document.org_id == current_user.org_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "id": str(document.document_id),
        "filename": document.filename,
        "document_type": document.document_type,
        "file_size": document.file_size_bytes,
        "content": document.content,
        "parties": document.parties or [],
        "created_at": document.created_at.isoformat(),
        "updated_at": document.updated_at.isoformat() if document.updated_at else None,
        "s3_key": document.s3_key
    }


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Delete a document"""
    document = db.query(Document).filter(
        Document.document_id == document_id,
        Document.org_id == current_user.org_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    db.delete(document)
    db.commit()

    return {"message": "Document deleted successfully"}
