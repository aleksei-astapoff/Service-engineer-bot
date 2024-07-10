import os

from dotenv import load_dotenv

from aiogram import F, types, Router
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query_client import (get_client_machines, orm_add_order,
                                       get_client_by_id)
from filters.chat_type import ChatTypeFilter
from keyboard import replay
from commands_bot.commands_bot_list import command_fsm
from utils import (create_message, reset_to_start_command,
                   bot_telegram, get_button_text)
from validators.validator import validator_phone_number

load_dotenv()

user_client_router = Router()

user_client_router.message.filter(ChatTypeFilter(['private']))


async def process_order(
        message: types.Message, state: FSMContext, session: AsyncSession):

    data = await state.get_data()

    try:
        order = await orm_add_order(session, data)

    except Exception as exc:
        order = None
        text = f'''
        Заявка не сохранена!
        Ошибка при сохранении заявки в Базу данных:
        {str(exc)}
        Обратитесь в службу поддержки.
        '''
        await message.bot.send_message(os.getenv('MANAGER_CHAT_ID'), text)

    await message.bot.send_message(
        os.getenv('MANAGER_CHAT_ID'),
        f'Заявка {"№ "+ str(order) if order else "" } на обработку')
    if data.get('repeat_application') is True:
        folder_path = data.get('machines_by_client').images
        text = f'Повторная заявка. Фото оборудования в папке: {folder_path}'
        await message.bot.send_message(os.getenv('MANAGER_CHAT_ID'), text)
    else:
        photos = data.get('image', [])
        for photo in photos:
            await message.bot.send_photo(os.getenv('MANAGER_CHAT_ID'), photo)

    application = create_message(data)

    await message.bot.send_message(os.getenv('MANAGER_CHAT_ID'), application)
    await state.clear()
    await message.answer(
        'Заявка оформлена. Менеджер свяжется с вами в ближайшее время.',
        reply_markup=replay.start_keyboard
    )
    await reset_to_start_command(message)


class RequestForService(StatesGroup):
    """Заказ Услуги"""

    type_service = State()
    type_machine = State()
    model_machine = State()
    serial_number = State()
    image = State()
    phone_number = State()
    address_service = State()
    repeat_application = State()
    repeat_application_step_2 = State()

    text = {
        'RequestForService:type_service': 'Выберите тип услуги.',
        'RequestForService:type_machine': 'Введите тип оборудования.',
        'RequestForService:model_machine': 'Введите модель оборудования.',
        'RequestForService:serial_number':
        'Введите серийный номер оборудования.',

        'RequestForService:image':
        'Добавьте фото оборудования не более 5 изображений',

        'RequestForService:phone_number': 'Введите ваш номер телефона.',
        'RequestForService:address_service': 'Введите ваш адрес.',
    }

    state_transitions = {
        'RequestForService:type_machine': 'RequestForService:type_service',
        'RequestForService:model_machine': 'RequestForService:type_machine',
        'RequestForService:serial_number': 'RequestForService:model_machine',
        'RequestForService:image': 'RequestForService:serial_number',
        'RequestForService:phone_number': 'RequestForService:image',
        'RequestForService:address_service': 'RequestForService:phone_number',
        'RequestForService.repeat_application': 'RequestForService:',
    }


@user_client_router.message(StateFilter(None),
                            or_f(Command('client_service'),
                            ((F.text.lower().contains('клиенту') | (
                             F.text.lower().contains('ремонт') | (
                              (F.text.lower().contains('то'))) | (
                              (F.text.lower().regexp(
                                  r'.*техническ[аиоеуюыь]?.*'))))))
        ))
async def service_cmd(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    """Обработка запроса клиента."""

    await bot_telegram.set_my_commands(
        commands=command_fsm,
        scope=types.BotCommandScopeChat(chat_id=message.chat.id)
        )
    client = await get_client_by_id(session, message.from_user.id)

    if client:
        machines_by_client = await get_client_machines(session, client)
        user_name = (
            message.from_user.first_name if message.from_user.first_name
            else message.from_user.username
        )
        await message.answer(
            f'Рад вас снова видеть {user_name}',
        )

        if machines_by_client:
            await message.answer(
                f'Колличество оборудования в базе: {len(machines_by_client)}',
            )
            await message.answer(
                'Хотите оформить повторную заявку?',
                reply_markup=replay.repeat_application_keyboard,
            )
            await state.update_data(machines_by_client=machines_by_client,
                                    client=client)
            await state.set_state(RequestForService.repeat_application)
    else:
        await state.set_state(RequestForService.type_service)
        await message.answer(
            'Что вас интересует? Для выхода воспльзутесь Меню',
            reply_markup=replay.client_keyboard,
            )


@user_client_router.message(RequestForService.repeat_application, F.text)
async def repeat_application(message: types.Message, state: FSMContext):
    """Обработка запроса клиента повторная заявка."""

    if message.text not in get_button_text(replay.repeat_application_keyboard):
        await message.answer(
            ('Пожалуйста, воспользуйтесь кнопками клавиатуры '
             'или Меню для выхода')
            )
    if message.text.casefold() == 'нет':
        await state.set_state(RequestForService.type_service)
        await message.answer(
            'Что вас интересует? Для выхода воспльзутесь Меню',
            reply_markup=replay.client_keyboard,
            )
    else:
        machines_by_client = (await state.get_data()).get('machines_by_client')
        list_machine = []
        for machine in machines_by_client:
            list_machine.append(machine.serial_number)
        button = [[KeyboardButton(text=row)] for row in list_machine]
        keyboard_list_machine = ReplyKeyboardMarkup(
            keyboard=button, resize_keyboard=True
            )
        await message.answer(
             'Выберите серийный оборудование для повторной заявки.',
             reply_markup=keyboard_list_machine
         )
        await state.update_data(keyboard_list_machine=keyboard_list_machine)
        await state.set_state(RequestForService.repeat_application_step_2)


@user_client_router.message(RequestForService.repeat_application_step_2,
                            F.text)
async def repeat_application_step_2(message: types.Message, state: FSMContext):
    """Обработка запроса клиента выбор оборудования."""

    if message.text not in get_button_text(
            (await state.get_data()).get('keyboard_list_machine')):
        await message.answer(
            ('Пожалуйста, воспользуйтесь кнопками клавиатуры '
             'или Меню для выхода')
            )
    else:
        machines_by_client = (await state.get_data()).get('machines_by_client')
        for machine in machines_by_client:
            if message.text == machine.serial_number:
                await state.update_data(machines_by_client=machine)
                break
        await message.answer(
            'Что вас интересует? Для выхода воспльзутесь Меню',
            reply_markup=replay.client_keyboard,
            )
        await state.set_state(RequestForService.type_service)


@user_client_router.message(RequestForService.type_service, F.text)
async def type_service(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    """Обработка запроса клиента тип услуги."""
    data = (await state.get_data()).get('keyboard_list_machine', None)

    if (
        message.text not in get_button_text(replay.client_keyboard)
        or message.text.casefold() == 'нет'
    ):
        await message.answer(
            ('Пожалуйста, воспользуйтесь кнопками клавиатуры '
             'или Меню для выхода')
            )
    elif data:
        await state.update_data(type_service=message.text,
                                repeat_application=True)
        await process_order(message, state, session)
    else:
        await state.update_data(type_service=message.text)
        await message.answer('Выберите тип установки.',
                             reply_markup=replay.client_service_keyboard)
        await state.set_state(RequestForService.type_machine)


@user_client_router.message(RequestForService.type_machine,
                            F.text == 'Другое оборудование')
async def type_machine_other(message: types.Message, state: FSMContext):
    """Обработка запроса клиента модель оборудования другог типа."""

    await state.update_data(other_machine_type=True)
    await message.answer('Введите тип установки.',
                         reply_markup=replay.del_keyboard)


@user_client_router.message(RequestForService.type_machine, F.text)
async def type_machine(message: types.Message, state: FSMContext):
    """Обработка запроса клиента сохранение типа оборудования."""

    data = await state.get_data()
    if ((message.text not in get_button_text(replay.client_service_keyboard)
         ) and ('other_machine_type' not in data)):
        await message.answer(
            ('Пожалуйста, воспользуйтесь кнопками клавиатуры '
             'или Меню для выхода')
            )
    else:
        await state.update_data(type_machine=message.text)
        await message.answer('Введите модель оборудования. Например: SDMO',
                             reply_markup=replay.del_keyboard)
        await state.set_state(RequestForService.model_machine)


@user_client_router.message(RequestForService.model_machine, F.text)
async def model_machine(message: types.Message, state: FSMContext):
    """Обработка запроса клиента сохранение модели оборудования."""

    await state.update_data(model_machine=message.text)
    await message.answer('Введите серийный номер.',
                         reply_markup=replay.del_keyboard)
    await state.set_state(RequestForService.serial_number)


@user_client_router.message(RequestForService.serial_number, F.text)
async def serial_number(message: types.Message, state: FSMContext):
    """Обработка запроса клиента сохранение Серийного номера оборудования."""

    await state.update_data(serial_number=message.text)
    await message.answer(
        'Добавьте фото серийных номеров оборудования. не более 5 изображений. '
        'Нажмите "Готово", чтобы пропустить.',
        reply_markup=replay.image_keyboard,)
    await state.set_state(RequestForService.image)


@user_client_router.message(RequestForService.image, F.photo)
async def image(message: types.Message, state: FSMContext):
    """Обработка запроса клиента сохранение фото не более 5."""

    user_data = await state.get_data()
    images_list = user_data.get('image', [])

    if len(images_list) < 5:
        images_list.append(message.photo[-1].file_id)
        await state.update_data(image=images_list)

        if len(images_list) == 5:
            await message.answer(
                ('Вы загрузили максимальное количество изображений. '
                    'Нажмите "Готово", чтобы продолжить.'),
                reply_markup=replay.image_keyboard)

        else:
            await message.answer(
                f'{len(images_list)} изображений сохранено. '
                f'Вы можете загрузить еще {5 - len(images_list)} изображений '
                f'или нажмите "Готово", чтобы продолжить.',
                reply_markup=replay.image_keyboard)

    else:
        await state.update_data(image=[])
        await message.answer(
            'Вы пытаетесь загрузить более 5 изображений.'
            'Обработка фото остановлена! Повторите загрузку.',
            reply_markup=replay.image_keyboard)


@user_client_router.message(RequestForService.image, F.text)
async def image_text_command(message: types.Message, state: FSMContext):
    """Обработка текстовых команд во время загрузки изображений."""

    if message.text.lower() == "готово":
        await message.answer(
            'Введите ваш номер телефона:',
            reply_markup=replay.phone_keyboard)
        await state.set_state(RequestForService.phone_number)
    else:
        await message.answer(
            'Если вы закончили загрузку изображений, нажмите "Готово".',
            reply_markup=replay.image_keyboard)


@user_client_router.message(RequestForService.phone_number,
                            F.text == 'Ввести вручную')
async def phone_number_manual(message: types.Message, state: FSMContext):
    """Обработка запроса клиента сохранение номера телефона вручную."""

    await message.answer(
        'Введите ваш номер телефона: Форма ввода 7 999 999 99 99 ',
        reply_markup=replay.del_keyboard
    )
    await state.set_state(RequestForService.phone_number)


@user_client_router.message(RequestForService.phone_number)
async def phone_number(message: types.Message, state: FSMContext):
    """Обработка запроса клиента сохранение номера телефона."""

    if message.contact:
        phone_number = message.contact.phone_number
    elif message.text:
        phone_number = message.text
    else:
        await message.answer(
            ('Пожалуйста, отправьте ваш номер телефона текстом '
             'или используйте кнопку для отправки контакта.'),
            reply_markup=replay.phone_keyboard)
        return
    phone_number = validator_phone_number(phone_number)
    if not phone_number:
        await message.answer(
            ('Введен не валидный номер телефона. Повторите ввод.'),
            reply_markup=replay.phone_keyboard)
        return

    await state.update_data(
        phone_number=phone_number,
        fist_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        telegram_profile_username=message.from_user.username,
        telegram_profile_id=message.from_user.id,
    )
    await message.answer(
        'Введите адрес оборудования.Форма ввода: Город, улица, дом',
        reply_markup=replay.del_keyboard,
        input_field_placeholder='Город, улица, номер дом или участка'
    )
    await state.set_state(RequestForService.address_service)


@user_client_router.message(RequestForService.address_service, F.text)
async def address_service(
        message: types.Message, state: FSMContext, session: AsyncSession
        ):
    """Обработка запроса клиента сохранение адреса оборудования."""

    await state.update_data(address_service=message.text)
    await process_order(message, state, session)
