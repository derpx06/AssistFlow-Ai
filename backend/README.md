# FastAPI Backend (Port of backend/)

## Setup

```bash
cd backend_fastapi
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 5001
```

API base: `http://127.0.0.1:5001/api`

## Notes

- MongoDB collections and indexes are initialized at startup.
- Socket.IO server is mounted at `/socket.io`.
- Knowledge/vector search uses Qdrant and local deterministic embeddings fallback.
