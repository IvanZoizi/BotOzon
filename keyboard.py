from aiogram import types

def get_start_kb():
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add(types.KeyboardButton(text="💰 Узнать цену на товар"))
    return keyboard