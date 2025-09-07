from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("⚽ Free", callback_data="plan_free"))
    kb.add(InlineKeyboardButton("💸 Pack 2€", callback_data="plan_2eur"))
    kb.add(InlineKeyboardButton("🏆 VIP", callback_data="plan_vip"))
    kb.add(InlineKeyboardButton("📋 Le mie schedine", callback_data="my_tickets"))
    return kb

def back_home():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("⬅️ Indietro", callback_data="back"))
    kb.add(InlineKeyboardButton("🏠 Home", callback_data="home"))
    return kb
