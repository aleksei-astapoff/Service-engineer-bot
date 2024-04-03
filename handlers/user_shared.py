from aiogram import F, types, Router
from aiogram.filters import CommandStart, Command, or_f

from filters.chat_type import ChatTypeFilter

from keyboard import replay
from utils import reset_to_start_command
# from constant import bot

user_router = Router()

user_router.message.filter(ChatTypeFilter(['private']))


@user_router.message(CommandStart())
async def start_cmd(message: types.Message):
    """Команда /start"""

    await reset_to_start_command(message)
    await message.answer(
        f'{message.from_user.first_name} приветсвую! '
        f'Я виртуальный помощник. Чем могу быть полезен?',
        reply_markup=replay.start_keyboard,

    )


@user_router.message(or_f(Command('menu'), (F.text.lower().contains('меню'))))
async def menu_cmd(message: types.Message):
    """Вызов основного меню бота"""

    await message.answer(
        'Выберите дальнейшее действие', reply_markup=replay.start_keyboard,
    )


@user_router.message(
        or_f(Command('about'),
             ((F.text.lower().contains('о продукте') | (
                 F.text.lower().contains('умеешь') | (
                     (F.text.lower().contains('можешь')))))))
    )
async def about_cmd(message: types.Message):
    """Сообщение о структуре бота"""

    await reset_to_start_command(message)
    await message.answer('Описание возможностей бота в разработке')
