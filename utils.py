import os
import pytz
from datetime import datetime
from aiogram import types, Bot
from commands_bot.commands_bot_list import command_list
from constant import TIME_ZONE

from dotenv import load_dotenv

load_dotenv()

TIME_ZONE = pytz.timezone(TIME_ZONE)

bot_telegram = Bot(token=os.getenv('BOT_TOKEN'))


def current_time():
    return datetime.now(TIME_ZONE)


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


def create_message(data):
    """Создание сообщения для заявки."""

    text = f'''
    Профиль: @{data.get('telegram_profile_id')}
    ФИО: {data.get('fist_name')} {data.get('last_name')}
    Номер телефона: +{data.get('phone_number')}
    Адрес оборудования: {data.get('address_machine')}
    Тип услуги: {data.get('type_service')}
    Тип оборудования: {data.get('type_machine')}
    Модель оборудования: {data.get('model_machine')}
    Серийный номер: {data.get('serial_number')}
    '''
    return text
