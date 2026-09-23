# Conversational RAG & Interview Booking API

FastAPI backend implementing document ingestion, custom RAG (Retrieval-Augmented Generation), Redis conversation memory, and LLM-powered interview booking — powered by Google Gemini, Qdrant, Redis, and SQLite.

---

## Features

- **Document Ingestion API**: PDF and TXT text extraction with support for selectable chunking strategies (`fixed_size` and `recursive`).
- **Custom RAG Pipeline**: Direct query embedding, Qdrant vector retrieval, context-augmented prompt construction, and Gemini response generation without high-level chain abstractions.
- **Multi-Turn Session Memory**: Redis-backed conversation history and booking state management with configurable session TTL.
- **LLM Interview Booking**: Automatic intent detection and multi-turn slot collection (`name`, `email`, `date`, `time`) persisted to SQLite.
- **Full Type Safety & Test Coverage**: Clean Python type annotations across all endpoints and services with pytest test coverage.

---

## Architecture Overview

```
                      +-------------------+
                      |   FastAPI App     |
                      +---------+---------+
                                |
             +------------------+------------------+
             |                                     |
  Document Ingestion API                    Conversational RAG API
  POST /api/v1/documents/upload            POST /api/v1/chat
             |                                     |
             v                                     v
      Text Extraction                       Intent Detection
     (PDF / TXT Parsing)                   (Question vs Booking)
             |                                     |
             v                             +-------+-------+
     Selectable Chunking                   |               |
   (fixed_size / recursive)                v               v
             |                        RAG Pipeline    Booking Flow
             v                             |               |
     Gemini Embeddings                     v               v
  (gemini-embedding-001)             Qdrant Search    Redis Session
             |                             |          (Field State)
             v                             v               |
       Qdrant Vector DB               Gemini LLM           v
             |                             |         SQLite Database
             v                             v          (Bookings Table)
      SQLite Metadata                 Redis Memory
    (Documents Table)                (History Log)
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Google Gemini API Key

---

### Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd rag_assisment
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set your Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **Start Infrastructure Services**
   ```bash
   docker compose up -d
   ```
   This starts:
   - **Qdrant Vector DB** on `http://localhost:6333`
   - **Redis Cache** on `localhost:6379`

4. **Install Dependencies**
   ```bash
   python -m venv .venv

   # On Windows:
   .venv\Scripts\activate

   # On Linux/macOS:
   source .venv/bin/activate

   pip install -r requirements.txt
   ```

5. **Run the Application**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   - API Base URL: `http://localhost:8000`
   - Interactive Swagger Docs: `http://localhost:8000/docs`

---

## API Documentation

### 1. Document Ingestion API

**Endpoint**: `POST /api/v1/documents/upload`  
**Content-Type**: `multipart/form-data`

**Parameters**:
- `file`: Upload file (`.pdf` or `.txt`)
- `chunking_strategy`: `fixed_size` or `recursive` (default: `recursive`)

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@sample.pdf" \
  -F "chunking_strategy=recursive"
```

**Example Response**:
```json
{
  "document_id": "8f3b2d1e-9a4c-4e11-823b-0123456789ab",
  "filename": "sample.pdf",
  "chunks": 12,
  "chunking_strategy": "recursive",
  "message": "Document ingested successfully"
}
```

---

### 2. Conversational RAG & Booking API

**Endpoint**: `POST /api/v1/chat`  
**Content-Type**: `application/json`

#### Document Question Query Example:
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-101",
    "message": "What technical skills are listed in the uploaded document?"
  }'
```

**Response**:
```json
{
  "answer": "Based on the uploaded document, the key skills listed are Python, FastAPI, SQL, and Qdrant.",
  "sources": [
    {
      "document_id": "8f3b2d1e-9a4c-4e11-823b-0123456789ab",
      "filename": "sample.pdf",
      "chunk_id": "c1a2b3d4-..."
    }
  ],
  "booking_id": null
}
```

#### Interview Booking Query Example:
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-102",
    "message": "I would like to book an interview. My name is Alex Smith, email alex@example.com, for 2026-10-15 at 14:00."
  }'
```

**Response**:
```json
{
  "answer": "Your interview has been booked!\n\nDetails:\n- Name: Alex Smith\n- Email: alex@example.com\n- Date: 2026-10-15\n- Time: 14:00\n\nBooking ID: 7684a0db-911a-4551-932e-99174dbd4995",
  "sources": [],
  "booking_id": "7684a0db-911a-4551-932e-99174dbd4995"
}
```

---

### 3. Get Booking Details API

**Endpoint**: `GET /api/v1/bookings/{booking_id}`

**Example Request**:
```bash
curl http://localhost:8000/api/v1/bookings/7684a0db-911a-4551-932e-99174dbd4995
```

**Example Response**:
```json
{
  "id": "7684a0db-911a-4551-932e-99174dbd4995",
  "name": "Alex Smith",
  "email": "alex@example.com",
  "date": "2026-10-15",
  "time": "14:00",
  "created_at": "2026-09-23T12:30:00"
}
```

---

## Testing

Run the full integration test suite with `pytest`:

```bash
pytest tests/ -v
```

All unit and endpoint tests run deterministically using mocked LLM/Vector responses and SQLite in-memory/file bindings.

---

## Technical Design Rationale

### Custom RAG vs High-Level Frameworks
Frameworks like LangChain add abstraction overhead and implicit magic. Building the RAG pipeline explicitly ensures full transparency over vector retrieval score thresholds, prompt context assembly, and exact control over conversation memory injection.

### Choice of Qdrant
Qdrant provides efficient cosine similarity vector indexing, automatic collection setup, payload-based metadata filters, and clean execution via a lightweight Docker image.

### Session Memory via Redis
Redis stores chat history and transient booking slot collection state. Using a time-to-live (`session_ttl`) mechanism ensures session state remains bounded without manual memory cleanup or database clutter.

### SQL Metadata Persistence
SQLAlchemy with SQLite provides schema validation and local persistence for document metadata and interview booking records without external database dependencies.

---

## Repository Structure

```
rag_assisment/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── chat.py           # Chat and booking endpoints
│   │       └── documents.py      # Document upload endpoint
│   ├── db/
│   │   ├── database.py           # SQLAlchemy engine & session factory
│   │   └── models.py             # Document & Booking database tables
│   ├── services/
│   │   ├── booking_service.py    # LLM booking extraction & storage
│   │   ├── chunking_service.py   # Fixed size & recursive text chunking
│   │   ├── document_service.py   # PDF and TXT text extraction
│   │   ├── embedding_service.py  # Gemini vector embeddings
│   │   ├── memory_service.py     # Redis chat history & booking state
│   │   ├── rag_service.py        # Custom RAG implementation
│   │   └── vector_service.py     # Qdrant collection & vector search
│   ├── config.py                 # Application settings loader
│   ├── main.py                   # FastAPI initialization & routes
│   └── schemas.py                # Pydantic request/response models
├── tests/
│   ├── conftest.py               # Test configuration & fixture hooks
│   ├── test_api.py               # API route integration tests
│   └── test_chunking.py          # Chunking strategy unit tests
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── README.md
└── requirements.txt
```
