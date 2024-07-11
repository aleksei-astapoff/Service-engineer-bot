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
    return datetime.now(TIME_ZONE).replace(microsecond=0)


def get_button_text(keyboard):
    return [button.text for row in keyboard.keyboard for button in row]


async def reset_to_start_command(message: types.Message):
    """Возврат к исходным командам на клавиатуре."""

    await bot_telegram.set_my_commands(
            commands=command_list,
            scope=types.BotCommandScopeChat(chat_id=message.chat.id)
        )


def create_message(data):
    """Создание сообщения для заявки."""

    client = data.get('client')
    machines_by_client = data.get('machines_by_client')

    text = f'''
    Профиль: @{data.get(
        'telegram_profile_id', client.telegram_profile_id if client else ''
        )}
    ФИО: {data.get('first_name', '')} {data.get(
        'last_name', client.full_name if client else ''
        )}
    Номер телефона: +{data.get(
        'phone_number', client.phone_number if client else ''
        )}
    Адрес оборудования: {data.get(
        'address_service', machines_by_client.address_machine
        if machines_by_client else ''
        )}
    Тип услуги: {data.get('type_service', '')}
    Тип оборудования: {data.get(
        'type_machine', machines_by_client.type_machine
        if machines_by_client else ''
        )}
    Модель оборудования: {data.get(
        'model_machine', machines_by_client.model_machine
        if machines_by_client else ''
        )}
    Серийный номер: {data.get(
        'serial_number', machines_by_client.serial_number
        if machines_by_client else ''
        )}
    '''
    return text


def unification_code_error(code_error):
    code_error = str(code_error)
    code_error = (
        code_error.replace(' ', '').replace('-', '').replace('(', '')
        .replace(')', '').replace('_', '').strip())
    return code_error


def create_message_error(code_error):
    """Создание сообщения для заявки."""

    type_equipment = ', '.join(
        set(str(model_equipment.producer_equipment.tupe_equipment)
            for model_equipment in code_error.model_equipments))

    producer_equipment = ', '.join(
        set(str(model_equipment.producer_equipment.producer_equipment)
            for model_equipment in code_error.model_equipments))

    model_equipment = ', '.join(
        set(str(model_equipment.model_equipment)
            for model_equipment in code_error.model_equipments))

    fmi = ', \n'.join(
        set(f'№ {fmi.fmi_number} - {fmi.text}'
            for fmi in code_error.fmi_numbers))

    text = f'''
    Данные по запросу:
    \nТип оборудования: {type_equipment}
    \nПроизводитель: {producer_equipment}
    \nМодель оборудования: {model_equipment}
    \nКод ошибки: {code_error.code_error}
    \nОшибка: {code_error.text_error}
    \nПеревод ошибки: {code_error.translation_text_error}
    \nВозможные FMI:
    \n{fmi if fmi else 'Нет данных о FMI в данном коде ошибки'}
    '''
    return text
