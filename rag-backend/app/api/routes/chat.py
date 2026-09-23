from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas import ChatRequest, ChatResponse, BookingResponse
from app.services import rag_service, booking_service, memory_service

router = APIRouter(tags=["Chat & Bookings"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    session_id, message = request.session_id, request.message
    in_booking = memory_service.get_booking_state(session_id)
    history = memory_service.get_history(session_id)

    if in_booking or booking_service.detect_intent(message, history) == "booking":
        answer, booking_id = booking_service.handle_booking(message, session_id, db)
        memory_service.add_message(session_id, "user", message)
        memory_service.add_message(session_id, "assistant", answer)
        return ChatResponse(answer=answer, sources=[], booking_id=booking_id)

    return rag_service.answer_question(message, session_id)


@router.get("/bookings/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: str, db: Session = Depends(get_db)) -> BookingResponse:
    booking = booking_service.get_booking(booking_id, db)
    if not booking:
        raise HTTPException(404, f"Booking '{booking_id}' not found")

    return BookingResponse(
        id=booking.id,
        name=booking.name,
        email=booking.email,
        date=booking.date.isoformat(),
        time=booking.time.strftime("%H:%M"),
        created_at=booking.created_at.isoformat(),
    )
