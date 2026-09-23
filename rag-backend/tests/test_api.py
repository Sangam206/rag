import io
from unittest.mock import MagicMock, patch
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.schemas import ChatResponse, SourceChunk


async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_txt_upload():
    with patch("app.api.routes.documents.embedding_service") as mock_embed, patch("app.api.routes.documents.vector_service") as mock_vector:
        mock_embed.embed_texts.return_value = [[0.1] * 768] * 3
        mock_vector.store_chunks.return_value = 3

        content = b"This is test content. " * 30
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/documents/upload",
                files={"file": ("test.txt", io.BytesIO(content), "text/plain")},
                data={"chunking_strategy": "recursive"},
            )

        assert response.status_code == 200
        body = response.json()
        assert body["filename"] == "test.txt"
        assert body["chunks"] > 0


async def test_reject_unsupported_file():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("photo.jpg", io.BytesIO(b"data"), "image/jpeg")},
            data={"chunking_strategy": "fixed_size"},
        )
    assert response.status_code == 400


async def test_chat_returns_answer():
    with patch("app.api.routes.chat.booking_service") as mock_booking, patch("app.api.routes.chat.rag_service") as mock_rag, patch("app.api.routes.chat.memory_service") as mock_memory:
        mock_memory.get_booking_state.return_value = None
        mock_memory.get_history.return_value = []
        mock_booking.detect_intent.return_value = "question"
        mock_rag.answer_question.return_value = ChatResponse(
            answer="The candidate knows Python.",
            sources=[SourceChunk(document_id="d1", filename="resume.pdf", chunk_id="c1")],
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/chat",
                json={"session_id": "test", "message": "What does the candidate know?"},
            )

        assert response.status_code == 200
        assert "answer" in response.json()
        assert len(response.json()["sources"]) > 0


async def test_booking_intent():
    with patch("app.api.routes.chat.booking_service") as mock_booking, patch("app.api.routes.chat.memory_service") as mock_memory:
        mock_memory.get_booking_state.return_value = None
        mock_memory.get_history.return_value = []
        mock_memory.add_message = MagicMock()
        mock_booking.detect_intent.return_value = "booking"
        mock_booking.handle_booking.return_value = ("What is your full name?", None)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/chat",
                json={"session_id": "test", "message": "I want to book an interview"},
            )

        assert response.status_code == 200
        assert "name" in response.json()["answer"].lower()


async def test_booking_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/bookings/fake-id")
    assert response.status_code == 404
