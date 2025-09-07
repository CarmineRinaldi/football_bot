from aiogram import types, Dispatcher
from .buttons import main_menu

WELCOME_TEXT = """
⚽ Benvenuto nel FootballBot! ⚽

Qui puoi ricevere pronostici vincenti per le tue schedine! 🎯
Scegli il tuo piano e preparati a segnare come CR7 🐐.

📌 Comandi principali:
- Free: fino a 5 match al giorno
- Pack 2€: 10 schedine
- VIP: accesso completo a tutti i pronostici

🏟️ Usa i pulsanti qui sotto per iniziare la partita!
"""

async def cmd_start(message: types.Message):
    await message.answer(WELCOME_TEXT, reply_markup=main_menu())

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=["start"])
