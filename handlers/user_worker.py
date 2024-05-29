from aiogram import F, types, Router
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from filters.chat_type import ChatTypeFilter
from keyboard import replay
from commands_bot.commands_bot_list import command_fsm
from utils import (reset_to_start_command, bot_telegram, get_button_text,
                   get_model_keyboard)

user_worker_router = Router()

user_worker_router.message.filter(ChatTypeFilter(['private']))


class RequestForHelpWorker(StatesGroup):
    """Заказ Услуги"""

    tupe_request = State()
    tupe_equiment = State()
    model_equiment = State()
    code_error = State()
    fmi_number = State()
    gost_step = State()
    finally_step = State()

    text = {
        'RequestForHelpWorker:tupe_request': 'Выберите тип запроса',
        'RequestForHelpWorker:tupe_equiment': 'Выберите тип оборудования',
        'RequestForHelpWorker:model_equiment': 'Выберите модель оборудования',
        'RequestForHelpWorker:code_error': 'Введите код ошибки',
        'RequestForHelpWorker:fmi_number': 'Введите FMI номер ошибки',
        'RequestForHelpWorker:gost_step': 'Выберите ГОСТ',
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
        # 'Выберете тип запроса. Для выхода воспльзутесь Меню',
        # reply_markup=replay.worker_keyboard
        'Данный раздел находится в разработке. Возвращаемся на главную.'
        )
    await state.set_state(RequestForHelpWorker.tupe_request)
    await message.answer(
        'Выберете тип запроса. Для выхода воспльзутесь Меню',
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
        'Отменена запроса', reply_markup=replay.start_keyboard
        )
    await reset_to_start_command(message)


@user_worker_router.message(StateFilter('*'), Command('back'))
@user_worker_router.message(StateFilter('*'), F.text.casefold() == 'назад')
async def back_cmd(message: types.Message, state: FSMContext):
    """Обработка запроса назад."""

    current_state = await state.get_state()
    if current_state == RequestForHelpWorker.tupe_request:
        await message.answer(
            'Предыдущего шага нет. Воспользуйтесь меню: "Отмена"'
            )
        return
    previous = None
    for step in RequestForHelpWorker.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            if previous.state == 'RequestForHelpWorker:tupe_request':
                keyboard = replay.worker_keyboard
            elif previous.state == 'RequestForHelpWorker:gost_step':
                keyboard = replay.gost_keyboard
            elif previous.state == 'RequestForHelpWorker:tupe_equiment':
                keyboard = replay.tupe_equiment_keyboard
            elif previous.state == 'RequestForHelpWorker:model_equiment':
                keyboard = replay.model_equiment_keyboard
            elif previous.state == 'RequestForHelpWorker:code_error':
                keyboard = replay.del_keyboard
            elif previous.state == 'RequestForHelpWorker:fmi_number':
                keyboard = replay.del_keyboard
            else:
                keyboard = replay.del_keyboard
            await message.answer(
                f'Вы вернулись к прошлому шагу: '
                f'{RequestForHelpWorker.text[previous.state]}',
                reply_markup=keyboard
            )
        previous = step


@user_worker_router.message(RequestForHelpWorker.tupe_request, F.text)
async def type_service(message: types.Message, state: FSMContext):
    """Обработка запроса сотрудника, тип запроса."""

    if message.text not in get_button_text(replay.worker_keyboard):
        await message.answer(
            ('Пожалуйста, воспользуйтесь кнопками клавиатуры '
             'или Меню для выхода')
            )
    elif message.text.casefold() == 'гост':
        await state.update_data(tupe_request=message.text)
        await message.answer('Выберите ГОСТ.',
                             reply_markup=replay.gost_keyboard)
        await state.set_state(RequestForHelpWorker.gost_step)
    else:
        await state.update_data(tupe_request=message.text)
        await message.answer('Выберите тип оборудования.',
                             reply_markup=replay.equiment_keyboard)
        await state.set_state(RequestForHelpWorker.tupe_equiment)


@user_worker_router.message(RequestForHelpWorker.gost_step, F.text)
async def gost(message: types.Message, state: FSMContext):
    """Обработка запроса сотрудника ГОСТ."""

    await state.update_data({})
    await message.answer('ГОСТы пока не загружены в Базу Данных',
                         reply_markup=replay.worker_keyboard)
    await state.set_state(RequestForHelpWorker.tupe_request)


@user_worker_router.message(RequestForHelpWorker.tupe_equiment, F.text)
async def type_equiment(message: types.Message, state: FSMContext):
    """Обработка запроса сотрудника тип оборудования."""

    if message.text not in get_button_text(replay.equiment_keyboard):
        await message.answer(
            ('Пожалуйста, воспользуйтесь кнопками клавиатуры '
             'или Меню для выхода')
            )
    else:
        await state.update_data(tupe_equiment=message.text)
        await message.answer('Выберите модель оборудования.')
        keyboard = get_model_keyboard(message.text)

        await message.answer(reply_markup=keyboard)
        await state.set_state(RequestForHelpWorker.model_equiment)
