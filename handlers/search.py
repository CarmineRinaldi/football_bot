from aiogram import types, Router
from .buttons import back_home
import asyncio
import random

WAIT_MESSAGES = [
    "🔍 Cercando la squadra come un difensore cerca di fermare Messi…",
    "🥅 Sto controllando i campionati come l’arbitro controlla il VAR…",
    "⚽ Analizzando i pronostici per te, non perdere la traversa!"
]

router = Router()

@router.message()
async def search_team(message: types.Message):
    msg = await message.answer(random.choice(WAIT_MESSAGES))
    await asyncio.sleep(1.5)
    await msg.delete()
    query = message.text
    # Simulazione risultati ricerca
    await message.answer(
        f"🔎 Risultati per '{query}':\n- Squadra 1\n- Squadra 2\n- Squadra 3",
        reply_markup=back_home()
    )

def register_handlers(dp):
    """Registra il router nel dispatcher"""
    dp.include_router(router)
