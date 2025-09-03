from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def start_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔥 Ricevi pronostici", callback_data="get_tip")],
        [InlineKeyboardButton("💳 Acquista pacchetto 10 pronostici", callback_data="buy_10")],
        [InlineKeyboardButton("👑 Abbonamento VIP", callback_data="vip")],
    ]
    return InlineKeyboardMarkup(keyboard)
