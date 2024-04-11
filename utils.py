import os
from aiogram import types, Bot
from commands_bot.commands_bot_list import command_list

from dotenv import load_dotenv

load_dotenv()

bot_telegram = Bot(token=os.getenv('BOT_TOKEN'))


def get_button_text(keyboard):
    return [button.text for row in keyboard.keyboard for button in row]


async def reset_to_start_command(message: types.Message):
    """Возврат к исходным командам на клавиатуре."""

    await bot_telegram.set_my_commands(
            commands=command_list,
            scope=types.BotCommandScopeChat(chat_id=message.chat.id)
        )


def get_model_keyboard(type_equiment):
    """Генерация клавиатуры для выбора модели оборудования."""

    if type_equiment == 'Панель управления':
        pass
    pass
