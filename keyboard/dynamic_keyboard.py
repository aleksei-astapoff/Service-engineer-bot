from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


from database.models_worker import Gost

DICT_MODEL_WORKER = {
    'гост': Gost.gost_shot_name
}


async def get_dynamic_keyboard(session: AsyncSession, data: str):
    """Получение динамической клавиатуры."""
    query = (
        await session.execute(select(DICT_MODEL_WORKER['гост']))
        ).scalars().all()
    button: list = [[KeyboardButton(text=row)] for row in query]

    keyboard = ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True)

    return keyboard
