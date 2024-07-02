from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


from database.models_worker import Gost


async def get_dynamic_keyboard(session: AsyncSession, data: str):
    """Получение динамической клавиатуры."""
    tupe_request = data.get('tupe_request')
    type_equipments = data.get('keyboard_type_equipments', None)
    producer_equipments = data.get('keyboard_producer_equipments', None)
    # code_errors = data.get('code_errors')
    if tupe_request == 'гост':
        query = (
            await session.execute(select(Gost.gost_shot_name))
            ).scalars().all()
        button: list = [[KeyboardButton(text=row)] for row in query]

        keyboard = ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True)

    elif tupe_request == 'коды ошибок' and not type_equipments:
        type_equipments = []
        for code_error in data.get('code_errors_type'):
            type_equipment = ', '.join(
                set(str(model_equipment.producer_equipment.tupe_equipment)
                    for model_equipment in code_error.model_equipments))
            if type_equipment not in type_equipments:
                type_equipments.append(type_equipment)
        button: list = [[KeyboardButton(text=row)] for row in type_equipments]

        keyboard = ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True)

    elif tupe_request == 'коды ошибок' and type_equipments and not producer_equipments:
        producer_equipments = []
        for code_error in data.get('code_errors_producer'):
            producer_equipment = ', '.join(
                set(str(model_equipment.producer_equipment.producer_equipment)
                    for model_equipment in code_error.model_equipments))
            if producer_equipment not in producer_equipments:
                producer_equipments.append(producer_equipment)
        button: list = [
            [KeyboardButton(text=row)] for row in producer_equipments
            ]
        keyboard = ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True)
    elif tupe_request == 'коды ошибок' and producer_equipments and type_equipments:
        model_equipments = []
        for code_error in data.get('code_errors_model'):
            model_equipment = ', '.join(
                set(str(model_equipment.model_equipment)
                    for model_equipment in code_error.model_equipments))
            if model_equipment not in model_equipments:
                model_equipments.append(model_equipment)
        button: list = [
            [KeyboardButton(text=row)] for row in model_equipments
            ]
        keyboard = ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True)

    return keyboard if keyboard else None
