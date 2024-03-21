from aiogram import F, types, Router
from aiogram.filters import CommandStart, Command, or_f

from filters.chat_type import ChatTypeFilter
from keyboard import replay

user_router = Router()

user_router.message.filter(ChatTypeFilter(['private']))


@user_router.message(CommandStart())
async def start_cmd(message: types.Message):
    """Команда /start"""

    await message.answer(
        f'{message.from_user.first_name} приветсвую! '
        f'Я виртуальный помощник. Чем могу быть полезен?',
        reply_markup=replay.start_keyboard,

    )


@user_router.message(or_f(Command('menu'), (F.text.lower().contains('меню'))))
async def menu_cmd(message: types.Message):
    """Вызов основного меню бота"""

    await message.answer(
        'Выберите действие.', reply_markup=replay.del_keyboard,
    )


@user_router.message(
        or_f(Command('about'),
             ((F.text.lower().contains('умеешь') | (
                 (F.text.lower().contains('можешь'))))))
    )
async def about_cmd(message: types.Message):
    """Сообщение о структуре бота"""

    await message.answer('О продукте')


@user_router.message(
        or_f(Command('error_code'),
             F.text.lower().regexp(r'.*ошиб[аикуеыо]?.*'))
    )
async def error_code_cmd(message: types.Message):
    """Обработка запроса: Коды ошибок"""

    await message.answer('Коды ошибок', )


@user_router.message(
        or_f(Command('service'),
             ((F.text.lower().contains('ремонт') | (
                 (F.text.lower().contains('то'))) | (
                     (F.text.lower().regexp(r'.*техническ[аиоеуюыь]?.*'))))))
        )
async def service_cmd(message: types.Message):
    """Обработка запроса клиента."""

    await message.answer(
        'Что вас интересует?', reply_markup=replay.client_keyboard,
        )
