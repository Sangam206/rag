from enum import Enum
from pydantic import BaseModel


class ChunkingStrategy(str, Enum):
    fixed_size = "fixed_size"
    recursive = "recursive"


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    chunks: int
    chunking_strategy: str
    message: str = "Document ingested successfully"


class SourceChunk(BaseModel):
    document_id: str
    filename: str
    chunk_id: str


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk] = []
    booking_id: str | None = None


class BookingResponse(BaseModel):
    id: str
    name: str
    email: str
    date: str
    time: str
    created_at: str
