from __future__ import annotations

import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from app.core.config import settings
from app.services.embeddings import embed_text, embed_many, VECTOR_SIZE


qdrant = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)


def knowledge_collection_name(company_id: int | None, website_id: int | None) -> str:
    c = f"c{company_id if company_id else 0}"
    w = f"w{website_id}" if website_id is not None else "default"
    return f"{settings.qdrant_collection}_{c}_{w}"


def _ensure_collection(name: str) -> None:
    existing = [c.name for c in qdrant.get_collections().collections]
    if name not in existing:
        qdrant.create_collection(name, vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE))


def upsert_ticket_vectors(rows: list[dict]) -> None:
    name = settings.qdrant_tickets_collection
    _ensure_collection(name)
    points = []
    vectors = embed_many([
        "\n".join([
            r.get("message", ""),
            f"Category: {r.get('category', '')}",
            f"Priority: {r.get('priority', '')}",
            f"Customer: {r.get('customerName', '')}",
        ]) for r in rows
    ])
    for i, row in enumerate(rows):
        points.append(PointStruct(id=str(uuid.uuid4()), vector=vectors[i], payload=row))
    qdrant.upsert(collection_name=name, points=points, wait=True)


def search_ticket_vectors(company_id: int, query: str, limit: int = 25) -> list[dict]:
    name = settings.qdrant_tickets_collection
    _ensure_collection(name)
    vec = embed_text(query)
    results = qdrant.search(
        collection_name=name,
        query_vector=vec,
        limit=limit,
        query_filter=Filter(must=[FieldCondition(key="companyId", match=MatchValue(value=company_id))]),
    )
    return [{"ticketId": str(r.payload.get("ticketId", r.id)), "score": float(r.score)} for r in results]


def upsert_knowledge_chunks(company_id: int, website_id: int | None, chunks: list[dict]) -> int:
    name = knowledge_collection_name(company_id, website_id)
    _ensure_collection(name)
    vectors = embed_many([c["content"] for c in chunks])
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vectors[i],
            payload={**chunks[i], "companyId": company_id, "websiteId": website_id},
        )
        for i in range(len(chunks))
    ]
    if points:
        qdrant.upsert(collection_name=name, points=points, wait=True)
    return len(points)


def search_knowledge(company_id: int, website_id: int | None, query: str, limit: int = 8) -> list[dict]:
    name = knowledge_collection_name(company_id, website_id)
    _ensure_collection(name)
    results = qdrant.search(collection_name=name, query_vector=embed_text(query), limit=limit, with_payload=True)
    out = []
    for r in results:
        p = r.payload or {}
        out.append({"content": p.get("content", ""), "source": p.get("source", ""), "title": p.get("title", "Untitled"), "score": float(r.score)})
    return out
