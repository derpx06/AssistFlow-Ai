from __future__ import annotations

import re
from app.db.mongo import get_db
from app.services.vector_store import search_knowledge


class RAGEngine:
    def triage_issue(self, query: str) -> dict:
        message = (query or "").strip()
        lower = message.lower()
        looks_like_issue = bool(re.search(r"error|issue|problem|bug|failed|unable|not working|billing|login|password|refund", lower))
        has_detail = len(message.split()) >= 6
        category = "billing" if re.search(r"billing|payment|refund|charge", lower) else "login" if re.search(r"login|password|auth", lower) else "technical" if re.search(r"error|bug|issue|failed|unable", lower) else "other"
        priority = "high" if re.search(r"urgent|blocked|cannot|can't|failed|error", lower) else "medium"
        summary = message[:140] + ("..." if len(message) > 140 else "")
        return {"shouldRaise": looks_like_issue and has_detail, "summary": summary, "category": category, "priority": priority, "urgency": priority, "message": message or "Customer reported an issue."}

    def answer_ticket(self, query: str, session_id: str = "default", company_id: int | None = None, website_id: int | None = None) -> dict:
        company_id = company_id or 1
        db = get_db()

        qa = db.questions.find_one({"companyId": company_id, "question": {"$regex": query, "$options": "i"}, "isActive": True})
        if qa:
            return {"answer": str(qa.get("answer", "")), "sources": [{"url": "Internal", "title": "Pre-defined Q&A"}], "type": "qa-match", "needs_handoff": False, "raise_ticket": False, "ticket_payload": None}

        docs = search_knowledge(company_id, website_id, query, 8)
        top = [d for d in docs if d["score"] > 0.55][:5]
        if not top:
            triage = self.triage_issue(query)
            return {
                "answer": "I may be missing complete context for this question. Please contact customer support.",
                "sources": [],
                "type": "rag-generation",
                "needs_handoff": True,
                "confidence": 0.0,
                "raise_ticket": triage["shouldRaise"],
                "ticket_payload": {
                    "summary": triage["summary"],
                    "category": triage["category"],
                    "priority": triage["priority"],
                    "urgency": triage["urgency"],
                    "customer_message": triage["message"],
                } if triage["shouldRaise"] else None,
            }

        context = "\n\n".join([d["content"][:300] for d in top])
        answer = f"Based on your docs: {context[:800]}"
        triage = self.triage_issue(query)
        sources = [{"url": d["source"], "title": d["title"], "score": d["score"]} for d in top]
        return {
            "answer": answer,
            "sources": sources,
            "type": "rag-generation",
            "needs_handoff": False,
            "confidence": min(0.99, top[0]["score"]),
            "raise_ticket": False,
            "ticket_payload": None,
        }


rag_engine = RAGEngine()
