from aiogram import F, types, Router
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from filters.chat_type import ChatTypeFilter
from keyboard import replay, dynamic_keyboard
from commands_bot.commands_bot_list import command_fsm
from utils import (reset_to_start_command, bot_telegram, get_button_text,
                   get_model_keyboard)
from database.orm_query_worker import orm_get_gost, orm_get_code_error

user_worker_router = Router()

user_worker_router.message.filter(ChatTypeFilter(['private']))


class RequestForHelpWorker(StatesGroup):
    """Заказ Услуги"""

    tupe_request = State()
    tupe_equipment = State()
    producer_equipment = State()
    model_equipment = State()
    code_error = State()
    fmi_number = State()
    gost_step = State()
    finally_step = State()

    text = {
        'RequestForHelpWorker:tupe_request': 'Выберите тип запроса',
        'RequestForHelpWorker:tupe_equipment': 'Выберите тип оборудования',
        'RequestForHelpWorker:model_equipment': 'Выберите модель оборудования',
        'RequestForHelpWorker:code_error': 'Введите код ошибки',
        'RequestForHelpWorker:fmi_number': 'Введите FMI номер ошибки',
        'RequestForHelpWorker:gost_step': 'Выберите ГОСТ',
    }

    state_transitions = {
        'RequestForHelpWorker:tupe_equipment': 'RequestForHelpWorker:tupe_request',
        'RequestForHelpWorker:model_equipment': 'RequestForHelpWorker:tupe_equipment',
        'RequestForHelpWorker:code_error': 'RequestForHelpWorker:model_equipment',
        'RequestForHelpWorker:fmi_number': 'RequestForHelpWorker:code_error',
        'RequestForHelpWorker:gost_step': 'RequestForHelpWorker:tupe_request',
        'RequestForHelpWorker:finally_step': 'RequestForHelpWorker:gost_step'
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
        return
    await state.clear()
    await message.answer(
        'Отмена запроса', reply_markup=replay.start_keyboard
        )
    await reset_to_start_command(message)

# @user_worker_router.message(StateFilter('*'), Command('back'))
# @user_worker_router.message(StateFilter('*'), F.text.casefold() == 'назад')
# async def back_cmd(message: types.Message, state: FSMContext):
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
    elif previous_state == 'RequestForHelpWorker:gost_step':
        keyboard = replay.del_keyboard
    elif previous_state == 'RequestForHelpWorker:tupe_equipment':
        keyboard = replay.tupe_equipment_keyboard
    elif previous_state == 'RequestForHelpWorker:model_equipment':
        keyboard = replay.model_equipment_keyboard
    elif previous_state == 'RequestForHelpWorker:code_error':
        keyboard = replay.del_keyboard
    elif previous_state == 'RequestForHelpWorker:fmi_number':
        keyboard = replay.del_keyboard
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
    elif message.text.casefold() == 'гост':
        await state.update_data(tupe_request=message.text.casefold())
        tupe_request = (await state.get_data()).get('tupe_request')
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
        await state.update_data(tupe_request=message.text)
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

    code_error = await orm_get_code_error(session, message.text)
    if len(code_error) == 1:
        await message.answer()
        await state.clear()
        await reset_to_start_command(message)
    else:
        await message.answer('Выберите тип оборудования.',)
        await state.update_data(code_error=code_error)
        await state.set_state(RequestForHelpWorker.tupe_equipment)
