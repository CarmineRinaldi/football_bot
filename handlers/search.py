from aiogram import types, Dispatcher
from .buttons import back_home
import asyncio
import random

# --- MESSAGGI DI ATTESA ---
WAIT_MESSAGES = [
    "🔍 Cercando la squadra come un difensore cerca di fermare Messi…",
    "🥅 Sto controllando i campionati come l’arbitro controlla il VAR…",
    "⚽ Analizzando i pronostici per te, non perdere la traversa!"
]

# --- HANDLER RICERCA ---
async def search_team(message: types.Message):
    msg = await message.answer(random.choice(WAIT_MESSAGES))
    await asyncio.sleep(1.5)
    await msg.delete()

    query = message.text.strip()
    await message.answer(
        f"🔎 Risultati per <b>{query}</b>:\n- Squadra 1\n- Squadra 2\n- Squadra 3",
        reply_markup=back_home()
    )

# --- REGISTRA HANDLER ---
def register_handlers(dp: Dispatcher):
    # Attivo solo se il messaggio contiene "cerca" o "search"
    dp.message.register(search_team, lambda m: "cerca" in m.text.lower() or "search" in m.text.lower())
