import asyncio

from aiogram import Dispatcher, types

from dotenv import load_dotenv

from constant import ALOWED_UPDATES
from handlers.user_shared import user_shared
from handlers.user_client import user_client_router
from handlers.user_worker import user_worker_router
from handlers.user_group import user_group_router
from commands_bot.commands_bot_list import command_list
from utils import bot_telegram

load_dotenv()


dp = Dispatcher()

dp.include_routers(user_client_router, user_worker_router,
                   user_group_router, user_shared)


async def main():
    """Запуск бота"""

    await bot_telegram.delete_webhook(drop_pending_updates=True)
    await bot_telegram.set_my_commands(
        commands=command_list, scope=types.BotCommandScopeAllPrivateChats()
        )
    await dp.start_polling(bot_telegram, allowed_updates=ALOWED_UPDATES)


asyncio.run(main())
