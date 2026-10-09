import hashlib
import uuid
from qdrant_client import QdrantClient, models
from sqlalchemy import select
from .config import settings
from .db import MemoryRecord, SessionLocal
from .model import embed

client = QdrantClient(url=settings.qdrant_url)

async def ensure_collection() -> None:
    # nomic-embed-text normally returns 768 dimensions. If the model changes, recreate
    # the collection deliberately rather than silently mixing incompatible vectors.
    if not client.collection_exists(settings.qdrant_collection):
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
        )

async def remember(text: str, source_url: str | None = None, source_title: str | None = None,
                   metadata: dict | None = None) -> dict:
    clean = text.strip()
    if not clean:
        raise ValueError("Memory text cannot be empty")
    digest = hashlib.sha256((clean + "\0" + (source_url or "")).encode()).hexdigest()
    record_id = str(uuid.uuid4())
    vector = await embed(clean)
    if len(vector) != 768:
        raise ValueError(f"Expected 768-dimensional embeddings, received {len(vector)}. Check OLLAMA_EMBED_MODEL.")
    with SessionLocal() as db:
        existing = db.scalar(select(MemoryRecord).where(MemoryRecord.content_hash == digest))
        if existing:
            return {"id": existing.id, "status": "duplicate", "source_url": existing.source_url}
        record = MemoryRecord(id=record_id, text=clean, source_url=source_url,
                              source_title=source_title, content_hash=digest,
                              metadata_json=metadata or {})
        db.add(record)
        db.commit()
    client.upsert(collection_name=settings.qdrant_collection, points=[models.PointStruct(
        id=record_id, vector=vector,
        payload={"memory_id": record_id, "source_url": source_url, "source_title": source_title,
                  "text": clean[:4000]},
    )])
    return {"id": record_id, "status": "stored", "source_url": source_url}

async def recall(query: str, limit: int | None = None) -> list[dict]:
    vector = await embed(query)
    results = client.query_points(collection_name=settings.qdrant_collection, query=vector,
                                  limit=limit or settings.memory_top_k, with_payload=True).points
    ids = [str(point.payload.get("memory_id")) for point in results if point.payload]
    if not ids:
        return []
    with SessionLocal() as db:
        records = {r.id: r for r in db.scalars(select(MemoryRecord).where(MemoryRecord.id.in_(ids))).all()}
    output = []
    for point in results:
        memory_id = str((point.payload or {}).get("memory_id", ""))
        record = records.get(memory_id)
        if record:
            output.append({"id": record.id, "text": record.text, "source_url": record.source_url,
                           "source_title": record.source_title, "score": point.score,
                           "created_at": record.created_at.isoformat()})
    return output
