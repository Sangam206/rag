import google.generativeai as genai

from app.config import settings
from app.services import embedding_service, vector_service, memory_service
from app.schemas import ChatResponse, SourceChunk

genai.configure(api_key=settings.gemini_api_key)
llm = genai.GenerativeModel(settings.llm_model)


def answer_question(question: str, session_id: str) -> ChatResponse:
    history = memory_service.get_history(session_id)
    query_vector = embedding_service.embed_query(question)
    results = vector_service.search_similar(query_vector, limit=settings.top_k)

    context = "\n\n---\n\n".join([r["text"] for r in results])
    history_text = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in history[-10:]])

    prompt = "You are a helpful assistant. Answer the question using ONLY the context below. If not present, say \"I don't have enough information to answer that.\"\n\n"
    prompt += f"CONTEXT:\n{context if context else 'No documents found.'}\n\n"
    if history_text:
        prompt += f"CONVERSATION HISTORY:\n{history_text}\n\n"
    prompt += f"QUESTION: {question}\n\nANSWER:"

    response = llm.generate_content(prompt)
    answer = response.text

    memory_service.add_message(session_id, "user", question)
    memory_service.add_message(session_id, "assistant", answer)

    sources = [
        SourceChunk(
            document_id=r["document_id"],
            filename=r["filename"],
            chunk_id=r["chunk_id"],
        )
        for r in results
    ]

    return ChatResponse(answer=answer, sources=sources)

