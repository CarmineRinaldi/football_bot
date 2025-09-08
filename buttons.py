from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Home / Menu principale
main_menu = InlineKeyboardMarkup()
main_menu.add(
    InlineKeyboardButton("Free", callback_data="menu_free"),
    InlineKeyboardButton("2€ Pack", callback_data="menu_2euro"),
    InlineKeyboardButton("VIP", callback_data="menu_vip"),
    InlineKeyboardButton("Le mie schedine", callback_data="my_tickets"),
    InlineKeyboardButton("Cerca", callback_data="search")
)

back_button = InlineKeyboardMarkup()
back_button.add(
    InlineKeyboardButton("🔙 Indietro", callback_data="back_home")
)
