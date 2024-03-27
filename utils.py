from aiogram import types
from commands_bot.commands_bot_list import command_list
from constant import bot_telegram


async def reset_to_start_command(message: types.Message):
    """Возврат к исходным командам на клавиатуре."""

    await bot_telegram.set_my_commands(
            commands=command_list,
            scope=types.BotCommandScopeChat(chat_id=message.chat.id)
        )
