import asyncio
import os

from aiogram import Bot, Dispatcher, types


from dotenv import load_dotenv

from constant import ALOWED_UPDATES
from handlers.user import user_router
from handlers.user_group import user_group_router
from commands_bot.commands_bot_list import user_list

load_dotenv()


bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

dp.include_routers(user_router, user_group_router)


async def main():
    """Запуск бота"""

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(
        commands=user_list, scope=types.BotCommandScopeAllPrivateChats()
        )
    await dp.start_polling(bot, allowed_updates=ALOWED_UPDATES)


asyncio.run(main())
