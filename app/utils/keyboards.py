from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Free"))
    kb.add(KeyboardButton("Pack 2€"))
    kb.add(KeyboardButton("VIP 4,99€/mese"))
    kb.add(KeyboardButton("Scegli Campionato"))
    kb.add(KeyboardButton("I miei pronostici"))
    kb.add(KeyboardButton("Supporto"))
    return kb

def back_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Indietro"))
    return kb
