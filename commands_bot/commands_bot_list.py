from aiogram.types import BotCommand


command_list = [
    BotCommand(command='menu', description='Главное меню.'),
    BotCommand(command='about', description='О нас'),
    BotCommand(command='client_service', description='Услуги клиентам'),
    BotCommand(command='worker', description='Сотрудникам'),
    BotCommand(command='cancel', description='Сбросить состояние'),
]

command_fsm = [
    BotCommand(command='cancel', description='Отмена'),
    BotCommand(command='back', description='Назад'),
]
