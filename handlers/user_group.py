from string import punctuation
from aiogram import types, Router, F

from constant import RESTRICTED_WORDS
from filters.chat_type import ChatTypeFilter

from database.load_data import load_data

user_group_router = Router()

user_group_router.message.filter(ChatTypeFilter(['group', 'supergroup']))


def clean_text(text: str):
    return text.translate(str.maketrans('', '', punctuation))


@user_group_router.message(F.text.lower().contains('обновить'))
async def update_code_error_in_db(message: types.Message):
    """Обновление кодов ошибок в базе данных."""
    try:
        await load_data()
        await message.answer('Обновление БД прошло успешно!')
    except Exception as exс:
        await message.answer(f'Произошла ошибка: {exс}')


@user_group_router.edited_message()
@user_group_router.message()
async def cleaner(message: types.Message):
    if RESTRICTED_WORDS.intersection(
        clean_text(message.text.lower()
                   ).split()):
        await message.answer(
            f'{message.from_user.first_name}, ведите себя прилично!'
        )
        await message.delete()
        # await message.chat.ban(message.from_user.id)
