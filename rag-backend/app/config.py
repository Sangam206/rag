from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Conversational RAG API"
    gemini_api_key: str = ""
    llm_model: str = "gemini-3.5-flash-lite"
    embedding_model: str = "gemini-embedding-001"
    embedding_dimension: int = 768

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "documents"
    redis_url: str = "redis://localhost:6379"
    database_url: str = "sqlite:///./app.db"

    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 5
    session_ttl: int = 3600

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
