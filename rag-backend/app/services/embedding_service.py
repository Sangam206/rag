import google.generativeai as genai

from app.config import settings

genai.configure(api_key=settings.gemini_api_key)

model_name = f"models/{settings.embedding_model}"
dimension = settings.embedding_dimension


def embed_texts(texts: list[str]) -> list[list[float]]:
    result = genai.embed_content(
        model=model_name,
        content=texts,
        task_type="retrieval_document",
        output_dimensionality=dimension,
    )
    return result["embedding"]


def embed_query(text: str) -> list[float]:
    result = genai.embed_content(
        model=model_name,
        content=text,
        task_type="retrieval_query",
        output_dimensionality=dimension,
    )
    return result["embedding"]
