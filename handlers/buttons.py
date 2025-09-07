from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Free", callback_data="plan_free"),
        InlineKeyboardButton("VIP", callback_data="plan_vip"),
        InlineKeyboardButton("Le mie schedine", callback_data="my_tickets")
    )
    return keyboard

def back_home():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🏠 Torna al menù principale", callback_data="back_home"))
    return keyboard
