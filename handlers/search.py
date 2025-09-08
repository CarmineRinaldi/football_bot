import asyncio
import random
from aiogram import Router, types
from ..buttons import back_home

router = Router()

WAIT_MESSAGES = [
    "🔍 Cercando la squadra come un difensore cerca di fermare Messi…",
    "🥅 Sto controllando i campionati come l’arbitro controlla il VAR…",
    "⚽ Analizzando i pronostici per te, non perdere la traversa!"
]

@router.message()
async def search_team(message: types.Message):
    msg = await message.answer(random.choice(WAIT_MESSAGES))
    await asyncio.sleep(1.5)
    await msg.delete()
    query = message.text
    await message.answer(
        f"🔎 Risultati per '{query}':\n- Squadra 1\n- Squadra 2\n- Squadra 3",
        reply_markup=back_home()
    )
