from aiogram import F, types, Router
from aiogram.filters import CommandStart, Command, or_f

user_router = Router()


@user_router.message(CommandStart())
async def start_cmd(message: types.Message):
    """Команда /start"""

    await message.answer(
        "Приветсвую! Я виртуальный помощник. Чем могу быть полезен?"
    )


@user_router.message(or_f(Command('menu'), (F.text.lower().contains('меню'))))
async def menu_cmd(message: types.Message):
    """Вызов основного меню бота"""

    await message.answer('Выберите действие.')


@user_router.message(
        or_f(Command('about'),
             ((F.text.lower().contains('умеешь') | (
                 (F.text.lower().contains('можешь'))))))
    )
async def about_cmd(message: types.Message):
    """Сообщение о структуре бота"""

    await message.answer('О нас') 


@user_router.message(
        or_f(Command('eror_code'),
             F.text.lower().regexp(r'.*ошибк[аиуеыо]?.*'))
    )
async def eror_code_cmd(message: types.Message):
    """Сообщение о структуре бота"""

    await message.answer('Коды ошибок')
