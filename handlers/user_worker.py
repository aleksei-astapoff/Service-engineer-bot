from aiogram import F, types, Router
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from filters.chat_type import ChatTypeFilter
from keyboard import replay, dynamic_keyboard
from commands_bot.commands_bot_list import command_fsm
from utils import (reset_to_start_command, bot_telegram, get_button_text,
                   create_message_error)
from database.orm_query_worker import orm_get_gost, orm_get_code_error

user_worker_router = Router()

user_worker_router.message.filter(ChatTypeFilter(['private']))


async def answer_request(message: types.Message, state: FSMContext, list_code_errors):
    """Ответ на заявку."""
    code_error = list_code_errors.pop()
    await message.answer(
        create_message_error(code_error),
        reply_markup=replay.start_keyboard)
    await state.clear()
    await reset_to_start_command(message)
    return


class RequestForHelpWorker(StatesGroup):
    """Заказ Услуги"""

    tupe_request = State()
    code_error = State()
    tupe_equipment = State()
    producer_equipment = State()
    model_equipment = State()
    gost_step = State()

    text = {
        'RequestForHelpWorker:tupe_request': 'Выберите тип запроса',
        'RequestForHelpWorker:tupe_equipment': 'Выберите тип оборудования',
        'RequestForHelpWorker:producer_equipment': 'Выберите производителя оборудования',
        'RequestForHelpWorker:model_equipment': 'Выберите модель оборудования',
        'RequestForHelpWorker:code_error': 'Введите код ошибки',
    }

    state_transitions = {
        'RequestForHelpWorker:tupe_equipment': 'RequestForHelpWorker:code_error',
        'RequestForHelpWorker:producer_equipment': 'RequestForHelpWorker:tupe_equipment',
        'RequestForHelpWorker:model_equipment': 'RequestForHelpWorker:producer_equipment',
        'RequestForHelpWorker:code_error': 'RequestForHelpWorker:tupe_request', # работает
        'RequestForHelpWorker:gost_step': 'RequestForHelpWorker:tupe_request', # работает
    }


@user_worker_router.message(
        StateFilter(None),
        or_f(Command('worker'),
             F.text.lower().contains('сотрудникам')))
async def error_code_cmd(message: types.Message, state: FSMContext):
    """Обработка запросов сотрудников"""

    await bot_telegram.set_my_commands(
        commands=command_fsm,
        scope=types.BotCommandScopeChat(chat_id=message.chat.id)
        )
    await state.set_state(RequestForHelpWorker.tupe_request)
    await message.answer(
        'Выберите тип запроса. Для выхода воспользуйтесь Меню',
        reply_markup=replay.worker_keyboard
    )


@user_worker_router.message(StateFilter('*'), Command('cancel'))
@user_worker_router.message(StateFilter('*'), F.text.casefold() == 'отмена')
async def cancel_cmd(message: types.Message, state: FSMContext):
    """Обработка запроса отмены."""

    current_state = await state.get_state()
    if current_state is None:
        await reset_to_start_command(message)
        await message.answer(
        'Отмена запроса', reply_markup=replay.start_keyboard
        )
        return
    await state.clear()
    await message.answer(
        'Отмена запроса', reply_markup=replay.start_keyboard
        )
    await reset_to_start_command(message)

@user_worker_router.message(StateFilter('*'), Command('back'))
@user_worker_router.message(StateFilter('*'), F.text.casefold() == 'назад')
async def back_cmd(message: types.Message, state: FSMContext):
    """Обработка запроса назад."""

    current_state = await state.get_state()

    previous_state = RequestForHelpWorker.state_transitions.get(current_state)

    if not previous_state:
        await message.answer(
            'Предыдущего шага нет. Воспользуйтесь меню: "Отмена"'
        )
        return

    await state.set_state(previous_state)

    # Выбор клавиатуры в зависимости от предыдущего состояния
    if previous_state == 'RequestForHelpWorker:tupe_request':
        keyboard = replay.worker_keyboard
    elif previous_state == 'RequestForHelpWorker:tupe_equipment':
        keyboard = (await state.get_data()).get('keyboard_type_equipments', replay.del_keyboard)
    elif previous_state == 'RequestForHelpWorker:producer_equipment':
        keyboard = (await state.get_data()).get('keyboard_producer_equipments', replay.del_keyboard)
    elif previous_state == 'RequestForHelpWorker:model_equipment':
        keyboard = (await state.get_data()).get('keyboard_model_equipment', replay.del_keyboard)
    elif previous_state == 'RequestForHelpWorker:code_error':
        keyboard = replay.del_keyboard
    elif previous_state == 'RequestForHelpWorker:gost_step':
        keyboard = (await state.get_data()).get('gost_keyboard', replay.del_keyboard)
    else:
        keyboard = replay.del_keyboard

    await message.answer(
        f'Вы вернулись к прошлому шагу: {RequestForHelpWorker.text[previous_state]}',
        reply_markup=keyboard
    )


@user_worker_router.message(RequestForHelpWorker.tupe_request, F.text)
async def type_service(
     message: types.Message, state: FSMContext, session: AsyncSession):
    """Обработка запроса сотрудника, тип запроса."""

    if message.text not in get_button_text(replay.worker_keyboard):
        await message.answer(
            ('Пожалуйста, воспользуйтесь кнопками клавиатуры '
             'или Меню для выхода')
            )
    else:
        await state.update_data(tupe_request=message.text.casefold())
        if message.text.casefold() == 'гост':
            tupe_request = await state.get_data()
            gost_keyboard = (
                await dynamic_keyboard.get_dynamic_keyboard(session, tupe_request)
                )
            await message.answer(
                'Выберите ГОСТ из списка.',
                reply_markup=gost_keyboard
                )
            await state.update_data(gost_keyboard=gost_keyboard)
            await state.set_state(RequestForHelpWorker.gost_step)
        else:
            await message.answer('Введите код ошибки.',
                                reply_markup=replay.del_keyboard)
            await state.set_state(RequestForHelpWorker.code_error)


@user_worker_router.message(RequestForHelpWorker.gost_step, F.text)
async def gost(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    """Обработка запроса сотрудника ГОСТ."""

    if message.text not in get_button_text(
        (await state.get_data()).get('gost_keyboard')
    ):
        await message.answer(
            ('Пожалуйста, воспользуйтесь кнопками клавиатуры '
             'или Меню для выхода')
            )
    else:
        gost = await orm_get_gost(session, message.text)
        message_gost = f'''
        Наименование: {gost.gost_shot_name}
        ГОСТ № {gost.gost_number}
        Описание: {gost.text}
        '''

        await message.answer(message_gost, reply_markup=replay.start_keyboard)
        await state.clear()
        await reset_to_start_command(message)


@user_worker_router.message(RequestForHelpWorker.code_error, F.text)
async def type_equipment(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    """Обработка запроса сотрудника тип оборудования."""

    data = await state.get_data()
    if data.get('keyboard_type_equipments', None):
        await state.update_data(keyboard_type_equipments=None)
        data = await state.get_data()
    list_code_errors = await orm_get_code_error(session, message.text)
    if len(list_code_errors) == 1:
        await answer_request(message, state, list_code_errors)
    elif not list_code_errors:
        await message.answer('Такого кода ошибки нет в базе данных.',
                             reply_markup=replay.start_keyboard)
        await state.clear()
        await reset_to_start_command(message)

    else:
        type_equipments = []
        for code_error in list_code_errors:
            type_equipment = ', '.join(
                set(str(model_equipment.producer_equipment.tupe_equipment)
                    for model_equipment in code_error.model_equipments))
            if type_equipment not in type_equipments:
                type_equipments.append(type_equipment)
        if len(type_equipments) != 1:
            await state.update_data(code_errors_type=list_code_errors)
            data = await state.get_data()

            keyboard_type_equipments = (
                await dynamic_keyboard.get_dynamic_keyboard(session, data)
            )
            await message.answer(
                'Выберите тип оборудования из списка.',
                reply_markup=keyboard_type_equipments
            )
            await state.update_data(
                keyboard_type_equipments=keyboard_type_equipments
                )
            await state.set_state(RequestForHelpWorker.tupe_equipment)


@user_worker_router.message(RequestForHelpWorker.tupe_equipment, F.text)
async def tupe_equipment(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    """Обработка запроса сотрудника тип оборудования."""

    data = await state.get_data()
    if data.get('keyboard_producer_equipments', None):
        await state.update_data(keyboard_producer_equipments=None)

    if message.text not in get_button_text(
     (await state.get_data()).get('keyboard_type_equipments')
    ):
        await message.answer(
            ('Пожалуйста, воспользуйтесь кнопками клавиатуры '
             'или Меню для выхода')
            )
    else:
        tupe_equipment_request = message.text
        code_errors = (await state.get_data()).get('code_errors_type')
        list_code_errors = []
        for code_error in code_errors:
            for model_equipment in code_error.model_equipments:
                tupe_equipment = (
                    model_equipment.producer_equipment.
                    tupe_equipment.type_equipment
                )
                if (
                    tupe_equipment == tupe_equipment_request
                    and code_error not in list_code_errors
                ):
                    list_code_errors.append(code_error)
        if len(list_code_errors) == 1:
            await answer_request(message, state, list_code_errors)
        else:
            await state.update_data(code_errors_producer=list_code_errors)
            keyboard_producer_equipments = (
                await dynamic_keyboard.get_dynamic_keyboard(
                    session, await state.get_data()
                    )
            )
            await message.answer(
                'Выберите производителя оборудования из списка.',
                reply_markup=keyboard_producer_equipments
            )
            await state.update_data(
                keyboard_producer_equipments=keyboard_producer_equipments
                )
            await state.set_state(RequestForHelpWorker.producer_equipment)


@user_worker_router.message(RequestForHelpWorker.producer_equipment, F.text)
async def producer_equipment(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    """Обработка запроса сотрудника производитель оборудования."""

    data = await state.get_data()
    if data.get('keyboard_model_equipment', None):
        await state.update_data(keyboard_model_equipment=None)
    if message.text not in get_button_text(
     (await state.get_data()).get('keyboard_producer_equipments')
    ):
        await message.answer(
            ('Пожалуйста, воспользуйтесь кнопками клавиатуры '
             'или Меню для выхода')
            )
    else:
        producer_equipment_request = message.text
        code_errors = (await state.get_data()).get('code_errors_producer')
        list_code_errors = []
        for code_error in code_errors:
            for model_equipment in code_error.model_equipments:
                producer_equipment = (
                    model_equipment.producer_equipment.producer_equipment
                    )
                if (
                    producer_equipment == producer_equipment_request
                    and code_error not in list_code_errors
                ):
                    list_code_errors.append(code_error)
        if len(list_code_errors) == 1:
            await answer_request(message, state, list_code_errors)
        else:
            await state.update_data(code_errors_model=list_code_errors)
            keyboard_model_equipment = (
                await dynamic_keyboard.get_dynamic_keyboard(
                    session, await state.get_data()
                    )
            )
            await message.answer(
                'Выберите модель оборудования из списка.',
                reply_markup=keyboard_model_equipment
            )
            await state.update_data(
                keyboard_model_equipment=keyboard_model_equipment
                )
            await state.set_state(RequestForHelpWorker.model_equipment)


@user_worker_router.message(RequestForHelpWorker.model_equipment, F.text)
async def model_equipment(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    """Обработка запроса сотрудника модель оборудования."""

    if message.text not in get_button_text(
     (await state.get_data()).get('keyboard_model_equipment')
    ):
        await message.answer(
            ('Пожалуйста, воспользуйтесь кнопками клавиатуры '
             'или Меню для выхода')
            )
    else:
        model_equipment_request = message.text
        code_errors = (await state.get_data()).get('code_errors_model')
        list_code_errors = []
        for code_error in code_errors:
            for model_equipment in code_error.model_equipments:
                model_equipment = (
                    model_equipment.model_equipment
                    )
                if (
                    model_equipment in model_equipment_request
                    and code_error not in list_code_errors
                ):
                    list_code_errors.append(code_error)
        for code_error in list_code_errors:
            await message.answer(
                create_message_error(code_error),
                )
        await state.clear()
        await reset_to_start_command(message)
        await message.answer('Запрос выполнен.',
                             reply_markup=replay.start_keyboard)
