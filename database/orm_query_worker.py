from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models_worker import Gost


async def orm_get_gost(session: AsyncSession, gost: str):
    """Получение ГОСТ из базы данных."""

    result = await session.execute(
        select(Gost).where(Gost.gost_shot_name == gost)
    )
    gost = result.scalar_one()

    return gost
