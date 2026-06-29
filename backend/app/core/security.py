from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(user_id: int, role: str, company_id: int) -> str:
    exp = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expires_in_hours)
    payload = {"sub": str(user_id), "role": role, "companyId": company_id, "exp": exp}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def create_widget_token(company_id: int, session_id: str, ticket_id: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(hours=settings.widget_jwt_expires_in_hours)
    payload = {
        "tokenType": "widget",
        "companyId": company_id,
        "sessionId": session_id,
        "ticketId": ticket_id,
        "exp": exp,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc
