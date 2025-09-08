from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Free")],
        [KeyboardButton(text="VIP")]
    ],
    resize_keyboard=True
)

plans_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Piano 1")],
        [KeyboardButton(text="Piano 2")]
    ],
    resize_keyboard=True
)
