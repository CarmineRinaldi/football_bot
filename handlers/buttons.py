from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# --- MENU PRINCIPALE ---
def main_menu():
    kb = [
        [KeyboardButton(text="📋 Le mie schedine")],
        [KeyboardButton(text="🎉 Piano Free"), KeyboardButton(text="🏆 Piano VIP")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# --- TORNA HOME ---
def back_home():
    kb = [
        [KeyboardButton(text="🏠 Torna al menu principale")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
