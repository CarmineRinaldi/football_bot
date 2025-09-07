from aiogram import types, Router
from aiogram.filters import Command
from .buttons import main_menu

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

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    """Handler per il comando /start"""
    await message.answer(WELCOME_TEXT, reply_markup=main_menu())

def register_handlers(dp):
    """Registra tutti gli handler di questo modulo"""
    dp.include_router(router)
