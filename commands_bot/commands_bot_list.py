from aiogram.types import BotCommand


user_list = [
    BotCommand(command='menu', description='Выберите действие.'),
    BotCommand(command='about', description='О нас'),
    BotCommand(command='error_code', description='Коды ошибок'),
    BotCommand(command='service', description='Услуги сервиса'),
]
