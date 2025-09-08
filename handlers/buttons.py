from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Free"), KeyboardButton(text="VIP")],
            [KeyboardButton(text="Le mie schedine")],
            [KeyboardButton(text="Cerca squadra")]
        ],
        resize_keyboard=True
    )

def back_home():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏠 Torna al menu")]
        ],
        resize_keyboard=True
    )
