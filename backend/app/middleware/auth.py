from fastapi import Header, HTTPException, Depends
from app.core.security import decode_token


def require_auth(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required.")
    token = authorization[7:]
    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")
    return {
        "userId": int(payload.get("sub")),
        "companyId": int(payload.get("companyId")),
        "role": payload.get("role"),
    }


def require_admin(auth: dict = Depends(require_auth)) -> dict:
    if auth.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    return auth
