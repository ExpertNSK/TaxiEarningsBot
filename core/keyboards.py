from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove)


def get_shift_keyboard():
    """Клавиатура для активной смены"""
    buttons = [
        [KeyboardButton(text='🏁 Завершить смену')]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder='Введи сумму заказа...'
    )
    return keyboard


def get_main_keyboard():
    """Главная клавиатура"""
    buttons = [
        [KeyboardButton(text='🚕 Начать смену')]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
    return keyboard


# Для удаления клавиатуры
remove_keyboard = ReplyKeyboardRemove()
