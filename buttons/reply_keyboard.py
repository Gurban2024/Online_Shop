from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


user_buttons = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Одежда')], [KeyboardButton(text='Обувь')],
        [KeyboardButton(text='Профиль')],
    ],
    resize_keyboard=True
)


admin_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Добавить позицию')], [KeyboardButton(text='Все позиции')], 
        [KeyboardButton(text='Изменить')], [KeyboardButton(text='Удалить')], [KeyboardButton(text='Список пользователей')]
    ],
    resize_keyboard=True
)
