from string import punctuation
from aiogram import types, Router

from constant import RESTRICTED_WORDS
from filters.chat_type import ChatTypeFilter

user_group_router = Router()

user_group_router.message.filter(ChatTypeFilter(['group', 'supergroup']))


def clean_text(text: str):
    return text.translate(str.maketrans('', '', punctuation))


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
