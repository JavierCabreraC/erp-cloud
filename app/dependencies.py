import os
from fastapi.security import APIKeyHeader
from fastapi import Security, HTTPException, status

from app.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

_api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(key: str = Security(_api_key_header)):
    if key != os.environ["API_KEY"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key inválida",
        )
