from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


from database.models_worker import Gost

DICT_MODEL_WORKER = {
    'гост': Gost.gost_shot_name
}


async def get_dynamic_keyboard(session: AsyncSession, data: str):
    """Получение динамической клавиатуры."""
    tupe_request = data.get('tupe_request')
    if tupe_request == 'гост':
        query = (
            await session.execute(select(DICT_MODEL_WORKER[tupe_request]))
            ).scalars().all()
        button: list = [[KeyboardButton(text=row)] for row in query]

        keyboard = ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True)

        return keyboard
    elif tupe_request == 'коды ошибок':
        code_errors = data.get('code_errors')
        type_equipments = []
        for code_error in code_errors:
            type_equipment = ', '.join(
                set(str(model_equipment.producer_equipment.tupe_equipment)
                    for model_equipment in code_error.model_equipments))
            if type_equipment not in type_equipments:
                type_equipments.append(type_equipment)
        button: list = [[KeyboardButton(text=row)] for row in type_equipments]

        keyboard = ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True)

        return keyboard