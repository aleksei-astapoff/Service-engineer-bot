
from aiogram import types
from aiogram.filters import Filter


class ChatTypeFilter(Filter):
    """Фильтрация типа чатов"""

    def __init__(self, chat_types: list[str]):
        self.chat_types = chat_types

    async def __call__(self, message: types.Message):
        return message.chat.type in self.chat_types
