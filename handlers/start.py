from aiogram import types, Dispatcher
from .buttons import main_menu

# --- TESTO DI BENVENUTO ---
WELCOME_TEXT = (
    "⚽ <b>Benvenuto nel FootballBot!</b> ⚽\n\n"
    "Qui puoi ricevere pronostici vincenti per le tue schedine! 🎯\n"
    "Scegli il tuo piano e preparati a segnare come CR7 🐐.\n\n"
    "📌 <b>Comandi principali:</b>\n"
    "- Free: fino a 5 match al giorno\n"
    "- Pack 2€: 10 schedine\n"
    "- VIP: accesso completo a tutti i pronostici\n\n"
    "🏟️ Usa i pulsanti qui sotto per iniziare la partita!"
)

# --- HANDLER /START ---
async def cmd_start(message: types.Message):
    await message.answer(WELCOME_TEXT, reply_markup=main_menu())

# --- REGISTRA HANDLER ---
def register_handlers(dp: Dispatcher):
    dp.message.register(cmd_start, commands=["start"])
