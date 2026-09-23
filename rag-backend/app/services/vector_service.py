import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.config import settings

client = QdrantClient(url=settings.qdrant_url)
collection = settings.qdrant_collection


def ensure_collection() -> None:
    collections = [c.name for c in client.get_collections().collections]
    if collection not in collections:
        client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=settings.embedding_dimension, distance=Distance.COSINE),
        )


def store_chunks(document_id: str, filename: str, chunks: list[str], embeddings: list[list[float]]) -> int:
    points = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        point_id = str(uuid.uuid4())
        point = PointStruct(
            id=point_id,
            vector=embedding,
            payload={
                "document_id": document_id,
                "filename": filename,
                "chunk_id": point_id,
                "chunk_index": i,
                "text": chunk,
            },
        )
        points.append(point)

    client.upsert(collection_name=collection, points=points)
    return len(points)


def search_similar(query_embedding: list[float], limit: int = 5) -> list[dict]:
    results = client.query_points(
        collection_name=collection,
        query=query_embedding,
        limit=limit,
        with_payload=True,
    )

    return [
        {
            "document_id": p.payload["document_id"],
            "filename": p.payload["filename"],
            "chunk_id": p.payload["chunk_id"],
            "text": p.payload["text"],
            "score": p.score,
        }
        for p in results.points
    ]

