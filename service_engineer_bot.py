import asyncio
import os

from aiogram import Dispatcher, types

from dotenv import load_dotenv

from constant import ALOWED_UPDATES, bot_telegram
from handlers.user_shared import user_router
from handlers.user_client import user_client_router
from handlers.user_worker import user_worker_router
from handlers.user_group import user_group_router
from commands_bot.commands_bot_list import command_list

load_dotenv()


dp = Dispatcher()

dp.include_routers(user_router, user_client_router, user_worker_router,
                   user_group_router,)


async def main():
    """Запуск бота"""

    await bot_telegram.delete_webhook(drop_pending_updates=True)
    await bot_telegram.set_my_commands(
        commands=command_list, scope=types.BotCommandScopeAllPrivateChats()
        )
    await dp.start_polling(bot_telegram, allowed_updates=ALOWED_UPDATES)


asyncio.run(main())
