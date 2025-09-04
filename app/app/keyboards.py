from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu():
kb = InlineKeyboardMarkup(row_width=2)
kb.add(
InlineKeyboardButton("🆓 Free (5)", callback_data="free"),
InlineKeyboardButton("💶 Pack 2€", callback_data="pack"),
)
kb.add(
InlineKeyboardButton("👑 VIP 4,99€/mese", callback_data="vip"),
InlineKeyboardButton("🏆 Scegli campionato", callback_data="choose_league"),
)
kb.add(
InlineKeyboardButton("📖 I miei pronostici", callback_data="my_picks"),
InlineKeyboardButton("⚙️ Impostazioni", callback_data="settings"),
)
return kb


def back_button(text="🔙 Indietro"):
kb = InlineKeyboardMarkup()
kb.add(InlineKeyboardButton(text, callback_data="back"))
return kb
