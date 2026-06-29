from __future__ import annotations

from datetime import datetime
from uuid import uuid4
from pymongo import MongoClient, ReturnDocument
from pymongo.database import Database
from app.core.config import settings


class Mongo:
    client: MongoClient | None = None
    db: Database | None = None


mongo = Mongo()


def connect_db() -> None:
    if mongo.db is not None:
        return
    mongo.client = MongoClient(settings.mongodb_uri)
    mongo.db = mongo.client[settings.mongodb_db_name]
    ensure_indexes()
    ensure_company_uuids()


def close_db() -> None:
    if mongo.client:
        mongo.client.close()
    mongo.client = None
    mongo.db = None


def get_db() -> Database:
    if mongo.db is None:
        connect_db()
    assert mongo.db is not None
    return mongo.db


def next_sequence(name: str) -> int:
    db = get_db()
    result = db.counters.find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return int(result["seq"])


def ensure_company_uuids() -> None:
    db = get_db()
    missing = db.companies.find(
        {"$or": [{"uuid": {"$exists": False}}, {"uuid": None}, {"uuid": ""}]},
        {"id": 1},
    )
    for company in missing:
      db.companies.update_one(
        {"id": company["id"]},
        {"$set": {"uuid": str(uuid4())}},
      )


def ensure_indexes() -> None:
    db = get_db()
    db.companies.create_index("id", unique=True)
    db.companies.create_index("uuid", unique=True, sparse=True)

    db.users.create_index("id", unique=True)
    db.users.create_index("email", unique=True)
    db.users.create_index("companyId")
    db.users.create_index("companyRoleId")

    db.company_roles.create_index("id", unique=True)
    db.company_roles.create_index([("companyId", 1), ("name", 1)], unique=True)

    db.api_keys.create_index("id", unique=True)
    db.api_keys.create_index("key", unique=True)
    db.api_keys.create_index("companyId")

    db.knowledge_sites.create_index("id", unique=True)
    db.knowledge_sites.create_index([("companyId", 1), ("baseUrl", 1)], unique=True)

    try:
        db.sitemaps.drop_index("companyId_1")
    except Exception:
        pass
    db.sitemaps.create_index([("companyId", 1), ("websiteId", 1)], unique=True)

    db.tickets.create_index([("companyId", 1), ("createdAt", -1)])
    db.tickets.create_index([("companyId", 1), ("status", 1), ("updatedAt", -1)])
    db.messages.create_index([("companyId", 1), ("ticketId", 1), ("createdAt", 1)])
    db.messages.create_index([("companyId", 1), ("sessionId", 1), ("createdAt", 1)])
    db.chat_sessions.create_index("sessionId", unique=True)
    db.chat_sessions.create_index([("companyId", 1), ("ticketId", 1)])


def test_db() -> None:
    db = get_db()
    ping = db.command({"ping": 1})
    if ping.get("ok") != 1:
        raise RuntimeError("Database ping failed")
