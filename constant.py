import os

from aiogram import Bot

from dotenv import load_dotenv

load_dotenv()

ALOWED_UPDATES = ['message, edited_message']

RESTRICTED_WORDS = {'толстяк', 'кабан', 'хомяк', }

bot_telegram = Bot(token=os.getenv('BOT_TOKEN'))

