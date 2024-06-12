from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_async_session
from database.models import Section
from themes.schemas import ThemeRead

router = APIRouter(
    prefix="/api/sections",
    tags=["Sections"]
)


@router.get("/", response_model=list[ThemeRead])
async def get_sections(
        session: AsyncSession = Depends(get_async_session)
):
    sections = await session.execute(select(Section))
    return sections.scalars().all()
