import json
import redis

from app.config import settings

redis_client = redis.from_url(settings.redis_url, decode_responses=True)
ttl = settings.session_ttl


def get_history(session_id: str) -> list[dict]:
    data = redis_client.get(f"chat:{session_id}")
    if data:
        return json.loads(data)
    return []


def add_message(session_id: str, role: str, content: str) -> None:
    key = f"chat:{session_id}"
    messages = get_history(session_id)
    messages.append({"role": role, "content": content})
    messages = messages[-20:]
    redis_client.set(key, json.dumps(messages))
    redis_client.expire(key, ttl)


def get_booking_state(session_id: str) -> dict | None:
    data = redis_client.get(f"booking:{session_id}")
    if data:
        return json.loads(data)
    return None


def save_booking_state(session_id: str, state: dict) -> None:
    key = f"booking:{session_id}"
    redis_client.set(key, json.dumps(state))
    redis_client.expire(key, ttl)


def clear_booking_state(session_id: str) -> None:
    redis_client.delete(f"booking:{session_id}")
