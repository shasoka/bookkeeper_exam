from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.connection import get_async_session
from database.models import Theme
from sections.schemas import SectionRead

router = APIRouter(
    prefix="/api/themes",
    tags=["Themes"]
)


# noinspection PyTypeChecker
@router.get("/", response_model=list[SectionRead])
async def get_themes(
        section_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    themes = await session.execute(select(Theme).where(Theme.section_id == section_id).options(selectinload(Theme.section)))
    return themes.scalars().all()
