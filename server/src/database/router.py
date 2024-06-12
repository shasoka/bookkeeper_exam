from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from database.connection import SessionLocal


router = APIRouter(
    prefix="/api/database",
    tags=["Database"]
)


@router.get("/ping", response_model=dict[str, str])
async def ping():
    async with SessionLocal() as session:
        async with session.begin():
            try:
                await session.execute(text("SELECT 1"))
                return {"detail": "Database is working"}
            except Exception:
                raise HTTPException(status_code=500, detail="Database is not responding")
