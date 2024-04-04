from aiogram.types import (KeyboardButton, KeyboardButtonPollType, # noqa
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
                text='Заявка на ремонт',
                # request_poll=KeyboardButtonPollType()
            ),
            KeyboardButton(
                text='Техническое обслуживание',
                # request_poll=KeyboardButtonPollType()
            ),
        ],
        [
            KeyboardButton(
                text='Консультация по оборудованию',
                # request_poll=KeyboardButtonPollType()
            ),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder='Чем мы можем вам помочь?',
)

client_service_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Генераторная установка'),
            KeyboardButton(text='Пожарный насос'),
        ],
        [
            KeyboardButton(text='Другое оборудование'),
        ],
    ],
    resize_keyboard=True,
)

image_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Готово',
                           resize_keyboard=True,
                           one_time_keyboard=True),
        ]
    ]
)

phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Отправить номер 📞', request_contact=True),
            KeyboardButton(text='Ввести вручную', request_contact=False),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder='Форма ввода +7 999 999 99 99',
)

worker_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Коды ошибок'),
            KeyboardButton(text='ГОСТ'),
        ]
    ],
    resize_keyboard=True,
)

gost_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Данных нет'),
        ]
    ],
)

equiment_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Панель управления'),
            KeyboardButton(text='Двигатель'),
        ]
    ],
    resize_keyboard=True,
)

model_equiment = ReplyKeyboardMarkup(
    keyboard=[
        [

        ]
    ]
)
