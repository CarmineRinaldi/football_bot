from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("Free pronostici", callback_data="free")],
        [InlineKeyboardButton("Compra 10 pronostici (2€)", callback_data="buy_10")],
        [InlineKeyboardButton("Abbonamento VIP 10 al giorno", callback_data="vip")],
    ]
    return InlineKeyboardMarkup(keyboard)
