from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_continue_dialog_keyboard():
    continue_button = InlineKeyboardButton(text='Continue dialog', callback_data='continue')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        continue_button
    ]])
    return keyboard


def get_stop_dialog_keyboard():
    continue_button = InlineKeyboardButton(text='Stop dialog', callback_data='stop')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        continue_button
    ]])
    return keyboard
