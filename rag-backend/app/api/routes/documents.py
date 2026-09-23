import uuid
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.db.database import get_db
from app.db.models import Document
from app.schemas import ChunkingStrategy, DocumentUploadResponse
from app.services import document_service, chunking_service, embedding_service, vector_service

router = APIRouter(tags=["Documents"])


@router.post("/documents/upload", response_model=DocumentUploadResponse)
def upload_document(
    file: UploadFile = File(...),
    chunking_strategy: ChunkingStrategy = Form(ChunkingStrategy.recursive),
    db: Session = Depends(get_db),
) -> DocumentUploadResponse:
    if not file.filename or not file.filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(400, "Only PDF and TXT files are supported")

    text, file_type = document_service.extract_text(file)
    if not text.strip():
        raise HTTPException(400, "No text extracted from file")

    chunks = chunking_service.chunk_text(
        text=text,
        strategy=chunking_strategy.value,
        chunk_size=settings.chunk_size,
        overlap=settings.chunk_overlap,
    )

    embeddings = embedding_service.embed_texts(chunks)
    document_id = str(uuid.uuid4())
    vector_service.store_chunks(
        document_id=document_id,
        filename=file.filename,
        chunks=chunks,
        embeddings=embeddings,
    )

    doc = Document(
        id=document_id,
        filename=file.filename,
        file_type=file_type,
        chunking_strategy=chunking_strategy.value,
        chunk_count=len(chunks),
    )
    db.add(doc)
    db.commit()

    return DocumentUploadResponse(
        document_id=document_id,
        filename=file.filename,
        chunks=len(chunks),
        chunking_strategy=chunking_strategy.value,
    )
