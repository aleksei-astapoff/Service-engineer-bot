from aiogram import F, types, Router
from aiogram.filters import Command, or_f

from filters.chat_type import ChatTypeFilter
from keyboard import replay

user_worker_router = Router()

user_worker_router.message.filter(ChatTypeFilter(['private']))


@user_worker_router.message(
            F.text.lower().contains('сотрудникам'))
async def staffer_cmd(message: types.Message):
    """Обработка запросов сотрудников"""

    await message.answer(
        'Данный раздел находится в разработке',
        # reply_markup=replay.worker_keyboard
        )


@user_worker_router.message(
        or_f(Command('worker'),
             F.text.lower().regexp(r'.*ошиб[аикуеыо]?.*'))
    )
async def error_code_cmd(message: types.Message):
    """Обработка запроса: Коды ошибок"""

    await message.answer(
        'Данный раздел находится в разработке',
        # reply_markup=replay.worker_keyboard
        )
