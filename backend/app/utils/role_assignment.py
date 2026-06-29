from app.db.mongo import get_db


CATEGORY_KEYWORDS = {
    "billing": ["billing", "payment", "invoice", "charge", "refund", "subscription"],
    "technical": ["technical", "tech", "engineering", "bug", "error", "issue", "crash", "outage"],
    "login": ["login", "signin", "sign in", "password", "reset", "auth", "access"],
    "other": ["support", "help", "general", "customer"],
}


def resolve_assigned_role(company_id: int, category: str | None, message: str | None) -> dict | None:
    db = get_db()
    roles = list(db.company_roles.find({"companyId": company_id}).sort("name", 1))
    if not roles:
        return None
    c = (category or "").lower().strip()
    words = set(CATEGORY_KEYWORDS.get(c, []))
    for w in (message or "").lower().split():
        if len(w) >= 4:
            words.add(w)

    def score(role: dict) -> int:
        text = f"{role.get('name','')} {role.get('description','')}".lower()
        s = 0
        if c and role.get("name", "").lower() == c:
            s += 4
        if c and c in text:
            s += 2
        s += sum(1 for w in words if w in text)
        return s

    best = max(roles, key=score)
    return {"id": best["id"], "name": best["name"]}
