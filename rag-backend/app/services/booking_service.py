import json
from datetime import date, time, datetime

import google.generativeai as genai
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.config import settings
from app.db.models import Booking
from app.services import memory_service

genai.configure(api_key=settings.gemini_api_key)
llm = genai.GenerativeModel(settings.llm_model)


def detect_intent(message: str, history: list[dict]) -> str:
    recent_history = json.dumps(history[-4:]) if history else "None"
    prompt = f"Decide if the user wants to BOOK/SCHEDULE an interview or ask a QUESTION.\nRecent history: {recent_history}\nUser message: {message}\nReply with exactly one word: booking or question"
    response = llm.generate_content(prompt)
    return "booking" if "booking" in response.text.strip().lower() else "question"


def handle_booking(message: str, session_id: str, db: Session) -> tuple[str, str | None]:
    state = memory_service.get_booking_state(session_id) or {"name": None, "email": None, "date": None, "time": None}

    extracted = extract_booking_fields(message, state)
    for field in ["name", "email", "date", "time"]:
        if extracted.get(field):
            state[field] = extracted[field]

    memory_service.save_booking_state(session_id, state)

    missing = [field for field in ["name", "email", "date", "time"] if not state[field]]

    if missing:
        questions = {
            "name": "Could you please provide your full name?",
            "email": "What email address should I use for the booking?",
            "date": "What date would you prefer for the interview?",
            "time": "What time works best for you?",
        }
        return questions[missing[0]], None

    booking_id = save_booking(session_id, state, db)
    memory_service.clear_booking_state(session_id)

    confirmation = f"Your interview has been booked!\n\nDetails:\n- Name: {state['name']}\n- Email: {state['email']}\n- Date: {state['date']}\n- Time: {state['time']}\n\nBooking ID: {booking_id}"
    return confirmation, booking_id


def extract_booking_fields(message: str, current_state: dict) -> dict:
    today_str = datetime.now().strftime("%Y-%m-%d")
    state_json = json.dumps(current_state)
    prompt = f"Extract booking information from this message.\nAlready collected: {state_json}\nToday is {today_str}.\nUser message: \"{message}\"\n\nReturn ONLY a JSON object with keys: name, email, date (YYYY-MM-DD), time (HH:MM).\nUse null for fields not present."
    response = llm.generate_content(prompt)
    try:
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(text)
    except Exception:
        return {}


def save_booking(session_id: str, state: dict, db: Session) -> str:
    try:
        booking_date = date.fromisoformat(state["date"])
    except Exception:
        booking_date = date.today()

    try:
        parts = state["time"].split(":")
        booking_time = time(int(parts[0]), int(parts[1]))
    except Exception:
        booking_time = time(9, 0)

    booking = Booking(
        session_id=session_id,
        name=state["name"],
        email=state["email"],
        date=booking_date,
        time=booking_time,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking.id


def get_booking(booking_id: str, db: Session) -> Booking | None:
    query = select(Booking).where(Booking.id == booking_id)
    return db.execute(query).scalar_one_or_none()

