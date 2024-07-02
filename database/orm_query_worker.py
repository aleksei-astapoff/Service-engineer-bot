from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models_worker import (CodeError, Gost, ModelEquipment,
                                    ProducerEquipment)
from utils import unification_code_error


async def orm_get_gost(session: AsyncSession, gost: str):
    """Получение ГОСТ из базы данных."""

    result = await session.execute(
        select(Gost).where(Gost.gost_shot_name == gost)
    )
    gost = result.scalar_one()

    return gost


async def orm_get_code_error(session: AsyncSession, code_error: str):
    """Получение кодов ошибок из базы данных."""

    unification_code = unification_code_error(code_error)
    result = (await session.execute(
        select(CodeError).options(
            selectinload(
                CodeError.model_equipments).selectinload(
                    ModelEquipment.producer_equipment).selectinload(
                        ProducerEquipment.tupe_equipment),
            selectinload(CodeError.fmi_numbers),
        ).where(CodeError.code_error == unification_code)
    )).scalars().all()
    print(result)
    return result
