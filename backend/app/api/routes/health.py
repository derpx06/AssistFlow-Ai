from fastapi import APIRouter
from app.db.mongo import test_db

router = APIRouter()


@router.get('/health')
def health():
    return {"success": True, "message": "ok"}


@router.get('/health/db')
def health_db():
    try:
        test_db()
        return {"success": True, "message": "db ok"}
    except Exception as e:
        return {"success": False, "message": "db unavailable", "error": str(e)}
