from aiogram import types, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from filters.chat_type import ChatTypeFilter
from handlers.user_worker import RequestForHelpWorker
from handlers.user_client import RequestForService
from utils import reset_to_start_command

from keyboard import replay

back_cancle_cmd_router = Router()
back_cancle_cmd_router.message.filter(ChatTypeFilter(['private']))

fist_steps = [
    RequestForHelpWorker.tupe_request, RequestForService.type_service,
    RequestForService.repeat_application
    ]


@back_cancle_cmd_router.message(StateFilter('*'), Command('cancel'))
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


@back_cancle_cmd_router.message(StateFilter('*'), Command('back'))
async def back_cmd(message: types.Message, state: FSMContext):
    """Обработка запроса назад."""

    # Определение текущего состояния
    current_state = await state.get_state()
    if not current_state or current_state in fist_steps:
        await message.answer(
            'Предыдущего шага нет. Воспользуйтесь меню: "Отмена"',
        )
        return

    # Определение предыдущего состояния для RequestForHelpWorker
    previous_state = RequestForHelpWorker.state_transitions.get(current_state)

    if previous_state:
        await state.set_state(previous_state)
        data = await state.get_data()
        if previous_state == 'RequestForHelpWorker:tupe_request':
            keyboard = replay.worker_keyboard
        elif previous_state == 'RequestForHelpWorker:tupe_equipment':
            keyboard = data.get(
                'keyboard_type_equipments', replay.del_keyboard
                )
        elif previous_state == 'RequestForHelpWorker:producer_equipment':
            keyboard = data.get(
                'keyboard_producer_equipments', replay.del_keyboard
                )
        elif previous_state == 'RequestForHelpWorker:model_equipment':
            keyboard = data.get(
                'keyboard_model_equipment', replay.del_keyboard
                )
        elif previous_state == 'RequestForHelpWorker:code_error':
            keyboard = replay.del_keyboard
        elif previous_state == 'RequestForHelpWorker:gost_step':
            keyboard = data.get('gost_keyboard', replay.del_keyboard)
        else:
            keyboard = replay.del_keyboard

        await message.answer(
            f'Вы вернулись к прошлому шагу: '
            f'{RequestForHelpWorker.text[previous_state]}',
            reply_markup=keyboard
        )
        return

    # Определение предыдущего состояния для RequestForService
    previous_state = RequestForService.state_transitions.get(current_state)

    if previous_state:
        await state.set_state(previous_state)
        data = await state.get_data()
        if previous_state == 'RequestForService:type_service':
            keyboard = replay.client_keyboard
        elif previous_state == 'RequestForService:type_machine':
            keyboard = replay.client_service_keyboard
        elif previous_state == 'RequestForService:model_machine':
            keyboard = replay.del_keyboard
        elif previous_state == 'RequestForService:serial_number':
            keyboard = replay.del_keyboard
        elif previous_state == 'RequestForService:image':
            keyboard = replay.image_keyboard
        elif previous_state == 'RequestForService:phone_number':
            keyboard = replay.phone_keyboard
        else:
            keyboard = replay.del_keyboard

        await message.answer(
            f'Вы вернулись к прошлому шагу: '
            f'{RequestForService.text[previous_state]}',
            reply_markup=keyboard
        )
        return
