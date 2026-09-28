from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from redis.exceptions import RedisError
from app.core.database import get_db
from app.core.redis import get_redis
from redis import Redis
from app.api.v1.router import router
from app.core.settings import settings
from app.schemas.health import HealthResponse
app = FastAPI(title="IVOIREX API", version="1.0.0", openapi_url="/api/v1/openapi.json")
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, allow_credentials=True, allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"], allow_headers=["Authorization", "Content-Type"])
app.include_router(router)
@app.get("/health", tags=["health"])
def health() -> HealthResponse:
    return HealthResponse(status="ok")
@app.get("/ready", tags=["health"])
def ready(db: Session = Depends(get_db), redis: Redis = Depends(get_redis)):
    db.execute(text("SELECT 1"))
    try:
        redis.ping()
    except RedisError as exc:
        raise HTTPException(status_code=503, detail="Redis unavailable") from exc
    return {"status": "ready"}
