from fastapi import FastAPI

from app.api.routes.documents import router as document_router
from app.api.routes.chat import router as chat_router
from app.db.database import init_db
from app.services.vector_service import ensure_collection

app = FastAPI(title="Conversational RAG API")


@app.on_event("startup")
def startup():
    init_db()
    ensure_collection()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


app.include_router(document_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
