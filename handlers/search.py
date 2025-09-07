from aiogram import types, Dispatcher
from .buttons import back_home

async def search_team(message: types.Message):
    query = message.text
    # Logica ricerca tramite API Football
    await message.answer(f"🔍 Risultati per '{query}':\n- Squadra 1\n- Squadra 2", reply_markup=back_home())

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(search_team, lambda m: True)  # Tutti i messaggi vengono considerati ricerche
