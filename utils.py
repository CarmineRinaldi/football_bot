import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def format_schedina(matches, odds):
    text = ""
    for i, m in enumerate(matches):
        text += f"{m['home']} vs {m['away']} | Quote: {odds[i]}\n"
    return text

def make_inline_keyboard(buttons):
    kb = [[InlineKeyboardButton(text=b[0], callback_data=b[1])] for b in buttons]
    return InlineKeyboardMarkup(kb)
