from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Free")],
        [KeyboardButton(text="Pack 2€")],
        [KeyboardButton(text="VIP")],
        [KeyboardButton(text="Le mie schedine")],
        [KeyboardButton(text="Cerca squadra")]
    ],
    resize_keyboard=True
)

back_home = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Indietro", callback_data="back"),
         InlineKeyboardButton(text="🏠 Home", callback_data="home")]
    ]
)
