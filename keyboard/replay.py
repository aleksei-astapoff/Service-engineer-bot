from aiogram.types import (KeyboardButton, KeyboardButtonPollType,
                           ReplyKeyboardMarkup, ReplyKeyboardRemove)


del_keyboard = ReplyKeyboardRemove()

start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Клиенту'),
            KeyboardButton(text='Сотрудникам'),
        ],
        [
            KeyboardButton(text='О продукте'),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder='Что вас интересует?',
)

client_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text='Создать заявку',
                request_poll=KeyboardButtonPollType()
            ),
        ],
        [
            KeyboardButton(text='Отправить номер 📞', request_contact=True),
            KeyboardButton(text='Местоположение 🗺️', request_location=True),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder='Чем мы можем вам помочь?',
)
