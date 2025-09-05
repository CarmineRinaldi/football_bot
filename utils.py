from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def make_inline_keyboard(buttons, row_width=2):
    kb = [[InlineKeyboardButton(text, callback_data=data) for text, data in buttons[i:i+row_width]] 
          for i in range(0, len(buttons), row_width)]
    return InlineKeyboardMarkup(kb)

def format_schedina(matches, odds):
    lines = []
    for m, o in zip(matches, odds):
        lines.append(f"{m['home']} vs {m['away']} → quota: {o}")
    return "\n".join(lines)
